use serde::{Serialize, Deserialize};

// ── 图谱 ──
#[derive(Serialize, Deserialize, Clone)]
pub struct Node {
    pub id: String,
    pub label: String,
    pub summary: String,
    pub links: Vec<String>,
    pub value: usize,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct Edge {
    pub from: String,
    pub to: String,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct GraphData {
    pub nodes: Vec<Node>,
    pub edges: Vec<Edge>,
    pub total_nodes: usize,
    pub mode: String,
}

// ── 统计 ──
#[derive(Serialize, Deserialize, Clone)]
pub struct StatusData {
    pub wiki_count: usize,
    pub archived_count: usize,
    pub total_count: usize,
    pub wiki_articles: Vec<String>,
    pub archived_articles: Vec<String>,
    #[serde(default)]
    pub link_count: usize,
    #[serde(default)]
    pub last_compile: String,
    #[serde(default)]
    pub chroma_available: bool,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct LinkInfo {
    pub from: String,
    pub to: String,
}

// ── 搜索 ──
#[derive(Serialize, Deserialize)]
pub struct SearchResult {
    pub title: String,
    pub preview: String,
    pub score: f64,
}

#[derive(Serialize, Deserialize)]
pub struct SearchResultData {
    pub results: Vec<SearchResult>,
    pub output: String,
    pub error: Option<String>,
}

#[derive(Serialize, Deserialize)]
pub struct AskResultData {
    pub answer: String,
    pub error: Option<String>,
}

// ── 上传/编译 ──
#[derive(Serialize, Deserialize)]
pub struct UploadResult {
    pub ok: bool,
    pub md_count: usize,
    pub other_count: usize,
    pub compiled: bool,
    pub note: String,
}

#[derive(Serialize, Deserialize)]
pub struct UploadFileData {
    pub file_name: String,
    pub data_base64: String,
}

#[derive(Serialize, Deserialize)]
pub struct CompileResult {
    pub ok: bool,
    pub converted: usize,
    pub output: String,
    pub error: Option<String>,
}

#[derive(Serialize, Deserialize)]
pub struct PendingFile {
    pub name: String,
    pub size: u64,
}

#[derive(Serialize, Deserialize)]
pub struct PendingResult {
    pub pending: Vec<PendingFile>,
    pub count: usize,
}

// ── 引擎状态 ──
#[derive(Serialize, Deserialize)]
pub struct EngineStatus {
    pub web_api: bool,
    pub chroma_available: bool,
}
