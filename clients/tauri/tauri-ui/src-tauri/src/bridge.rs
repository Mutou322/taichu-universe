use crate::types::*;

/// 判断 Web API 是否可用
pub fn check_health() -> bool {
    std::net::TcpStream::connect_timeout(
        &"127.0.0.1:8765".parse().unwrap(),
        std::time::Duration::from_secs(2),
    )
    .is_ok()
}

/// 知识库状态（从 Web API 获取）
pub fn get_stats_blocking() -> StatusData {
    match ureq::get("http://127.0.0.1:8765/api/stats").call() {
        Ok(resp) => resp.into_json().unwrap_or(StatusData {
            wiki_count: 0, archived_count: 0, total_count: 0,
            wiki_articles: vec![], archived_articles: vec![],
            link_count: 0, last_compile: "".to_string(), chroma_available: false,
        }),
        Err(_) => StatusData {
            wiki_count: 0, archived_count: 0, total_count: 0,
            wiki_articles: vec![], archived_articles: vec![],
            link_count: 0, last_compile: "".to_string(), chroma_available: false,
        },
    }
}

/// 图谱数据（从 Web API 获取）
pub fn get_graph_blocking(limit: usize) -> GraphData {
    let url = format!("http://127.0.0.1:8765/api/kb/graph?limit={}", limit);
    match ureq::get(&url).call() {
        Ok(resp) => resp.into_json().unwrap_or(GraphData {
            nodes: vec![], edges: vec![], total_nodes: 0, mode: "error".into(),
        }),
        Err(_) => GraphData {
            nodes: vec![], edges: vec![], total_nodes: 0, mode: "error".into(),
        },
    }
}

/// 待处理文件列表
pub fn get_pending_blocking() -> PendingResult {
    match ureq::get("http://127.0.0.1:8765/api/kb/pending").call() {
        Ok(resp) => resp.into_json().unwrap_or(PendingResult { pending: vec![], count: 0 }),
        Err(_) => PendingResult { pending: vec![], count: 0 },
    }
}
