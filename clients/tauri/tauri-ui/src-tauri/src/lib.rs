pub mod types;
pub mod bridge;
pub mod kb;

use types::*;
use kb::KnowledgeBase;
use tauri::{Emitter, Manager};

fn get_local_kb() -> KnowledgeBase {
    let home = std::env::var("HOME").unwrap_or_default();
    KnowledgeBase::new(
        &format!("{}/taichu/knowledge/wiki", home),
        &format!("{}/taichu/ingest/raw", home),
        &format!("{}/taichu/knowledge/wiki/_archived", home),
    )
}

#[tauri::command]
fn get_graph(limit: Option<usize>) -> GraphData {
    let data = bridge::get_graph_blocking(limit.unwrap_or(150));
    if data.nodes.is_empty() && data.mode == "error" {
        get_local_kb().build_graph(limit.unwrap_or(150))
    } else {
        data
    }
}

#[tauri::command]
fn get_status() -> StatusData {
    let data = bridge::get_stats_blocking();
    if data.total_count == 0 && data.wiki_articles.is_empty() {
        get_local_kb().get_status()
    } else {
        data
    }
}

#[tauri::command]
fn get_pending() -> PendingResult {
    bridge::get_pending_blocking()
}

#[tauri::command]
fn get_engine_status() -> EngineStatus {
    EngineStatus {
        web_api: bridge::check_health(),
        chroma_available: true,
    }
}

/// 上传文件（通过 HTTP API 转发，接收文件路径）
#[tauri::command]
async fn upload_file(path: String) -> UploadResult {
    eprintln!("[upload_file] called with path: {}", path);
    use std::path::Path;
    let file_path = Path::new(&path);
    if !file_path.exists() {
        eprintln!("[upload_file] file not found: {}", path);
        return UploadResult {
            ok: false, md_count: 0, other_count: 0, compiled: false,
            note: format!("文件不存在: {}", path),
        };
    }

    let ext = file_path.extension()
        .map(|e| format!(".{}", e.to_string_lossy().to_lowercase()))
        .unwrap_or_default();
    let supported = [".md", ".pdf", ".docx", ".pptx", ".xls", ".xlsx", ".html", ".htm", ".txt",
                     ".csv", ".json", ".xml", ".rtf", ".epub",
                     ".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".svg",
                     ".py", ".js", ".ts", ".rs", ".c", ".cpp", ".h", ".java", ".go", ".rb", ".sh", ".yaml", ".toml",
                     ".zip", ".tar", ".gz", ".7z", ".rar",
                     ".doc", ".ppt",
                     ".wasm", ".markdown"];
    if !supported.contains(&ext.as_str()) {
        return UploadResult {
            ok: false, md_count: 0, other_count: 0, compiled: false,
            note: format!("不支持的文件格式: {}", ext),
        };
    }

    let content = match std::fs::read(&path) {
        Ok(c) => c,
        Err(e) => return UploadResult {
            ok: false, md_count: 0, other_count: 0, compiled: false,
            note: format!("文件读取失败: {}", e),
        },
    };

    let name = file_path.file_name().unwrap().to_string_lossy().to_string();
    let mime = match ext.as_str() {
        ".md" => "text/markdown",
        ".pdf" => "application/pdf",
        ".png" => "image/png",
        ".jpg" | ".jpeg" => "image/jpeg",
        ".webp" => "image/webp",
        ".gif" => "image/gif",
        ".bmp" => "image/bmp",
        ".py" => "text/x-python",
        ".js" => "text/javascript",
        ".ts" => "text/typescript",
        ".yaml" | ".toml" => "text/plain",
        ".html" => "text/html",
        ".csv" => "text/csv",
        ".json" => "application/json",
        ".xml" => "application/xml",
        _ => "application/octet-stream",
    };
    let name_for_part = name.clone();
    let part = reqwest::multipart::Part::bytes(content)
        .file_name(name_for_part)
        .mime_str(mime)
        .unwrap();

    let form = reqwest::multipart::Form::new()
        .part("files", part);

    match reqwest::Client::new()
        .post("http://127.0.0.1:8765/upload")
        .multipart(form)
        .send()
        .await
    {
        Ok(resp) => {
            let status = resp.status();
            eprintln!("[upload_file] HTTP {} from API server", status);
            match resp.json::<serde_json::Value>().await {
                Ok(json) => {
                    eprintln!("[upload_file] API response: {:?}", json);
                    UploadResult {
                        ok: json.get("ok").and_then(|v| v.as_bool()).unwrap_or(false),
                        md_count: json.get("md_count").and_then(|v| v.as_u64()).unwrap_or(0) as usize,
                        other_count: json.get("other_count").and_then(|v| v.as_u64()).unwrap_or(0) as usize,
                        compiled: json.get("compiled").and_then(|v| v.as_bool()).unwrap_or(false),
                        note: json.get("note").and_then(|v| v.as_str()).unwrap_or("上传完成").to_string(),
                    }
                }
                Err(e) => UploadResult {
                    ok: false, md_count: 0, other_count: 0, compiled: false,
                    note: format!("上传响应解析失败: {}", e),
                },
            }
        }
        Err(e) => UploadResult {
            ok: false, md_count: 0, other_count: 0, compiled: false,
            note: format!("上传失败: {}", e),
        },
    }
}

/// 上传文件数据（接收 base64 编码的文件内容，供前端点击选择文件时使用）
#[tauri::command]
async fn upload_file_data(data: UploadFileData) -> UploadResult {
    eprintln!("[upload_file_data] received: {} ({} bytes base64)", data.file_name, data.data_base64.len());
    // 把 base64 解码后写入临时文件，再调 upload_file 逻辑
    use std::io::Write;
    use base64::Engine;
    let bytes = match base64::engine::general_purpose::STANDARD.decode(&data.data_base64) {
        Ok(b) => b,
        Err(e) => return UploadResult {
            ok: false, md_count: 0, other_count: 0, compiled: false,
            note: format!("base64 解码失败: {}", e),
        },
    };
    let tmp_dir = std::env::temp_dir();
    let tmp_path = tmp_dir.join(&data.file_name);
    match std::fs::File::create(&tmp_path) {
        Ok(mut f) => {
            if let Err(e) = f.write_all(&bytes) {
                return UploadResult {
                    ok: false, md_count: 0, other_count: 0, compiled: false,
                    note: format!("临时文件写入失败: {}", e),
                };
            }
        }
        Err(e) => return UploadResult {
            ok: false, md_count: 0, other_count: 0, compiled: false,
            note: format!("临时文件创建失败: {}", e),
        },
    }
    let path_str = tmp_path.to_string_lossy().to_string();
    let result = upload_file(path_str).await;
    // 清理临时文件
    let _ = std::fs::remove_file(&tmp_path);
    result
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .setup(|app| {
            // 获取主窗口，监听原生拖放事件
            if let Some(window) = app.get_webview_window("main") {
                let w = window.clone();
                window.on_window_event(move |event| {
                    if let tauri::WindowEvent::DragDrop(drag_event) = event {
                        match drag_event {
                            tauri::DragDropEvent::Enter { paths, .. } => {
                                let _ = w.emit("tauri-drag-enter", paths.clone());
                            }
                            tauri::DragDropEvent::Over { position, .. } => {
                                let _ = w.emit("tauri-drag-over", serde_json::json!({"x": position.x, "y": position.y}));
                            }
                            tauri::DragDropEvent::Drop { paths, .. } => {
                                let _ = w.emit("tauri-drag-drop", paths.clone());
                            }
                            tauri::DragDropEvent::Leave => {
                                let _ = w.emit("tauri-drag-leave", "");
                            }
                            _ => {}
                        }
                    }
                });
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            get_graph, get_status, get_pending, get_engine_status,
            upload_file, upload_file_data,
        ])
        .run(tauri::generate_context!())
        .expect("failed to run Tauri app");
}
