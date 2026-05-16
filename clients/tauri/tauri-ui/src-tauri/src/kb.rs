use crate::types::*;
use regex::Regex;
use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};
use chrono::{DateTime, Local};

pub struct KnowledgeBase {
    pub wiki_dir: PathBuf,
    pub raw_dir: PathBuf,
    pub archived_dir: PathBuf,
}

impl KnowledgeBase {
    pub fn new(wiki: &str, raw: &str, archived: &str) -> Self {
        Self {
            wiki_dir: PathBuf::from(wiki),
            raw_dir: PathBuf::from(raw),
            archived_dir: PathBuf::from(archived),
        }
    }

    /// 遍历 wiki 目录构建 graph（兼容 Web API 的 string ID 格式）
    pub fn build_graph(&self, limit: usize) -> GraphData {
        let mut nodes_map: HashMap<String, Node> = HashMap::new();
        let mut edge_set: HashMap<String, bool> = HashMap::new();
        let mut edges: Vec<Edge> = Vec::new();

        let md_files: Vec<PathBuf> = walkdir(&self.wiki_dir, 1)
            .into_iter()
            .chain(walkdir(&self.archived_dir, 3))
            .collect();

        for file in &md_files {
            let stem_orig = file.file_stem().unwrap().to_string_lossy().to_string();
            if stem_orig == "index" { continue; }
            let content = fs::read_to_string(file).unwrap_or_default();
            let links = extract_wikilinks(&content);
            let summary = extract_summary(&content);
            let value = links.len().max(1);

            let node = Node {
                id: stem_orig.clone(),
                label: stem_orig.clone(),
                summary,
                links: links.iter().map(|l| l.split('|').next().unwrap_or(l).trim().to_string()).collect(),
                value,
            };
            nodes_map.insert(node.id.clone(), node);

            for link in &links {
                let target = link.split('|').next().unwrap_or(link).trim().to_string();
                let ek = sorted_key(&stem_orig, &target);
                if !edge_set.contains_key(&ek) {
                    edge_set.insert(ek.clone(), true);
                    edges.push(Edge { from: stem_orig.clone(), to: target });
                }
            }
        }

        // 添加被引用但未创建的节点
        for edge in &edges {
            for role in [&edge.from, &edge.to] {
                if !nodes_map.contains_key(role) {
                    nodes_map.insert(role.clone(), Node {
                        id: role.clone(),
                        label: role.clone(),
                        summary: "(被引用但未创建)".to_string(),
                        links: vec![],
                        value: 1,
                    });
                }
            }
        }

        // 按 degree 排序取 top
        let mut degree: HashMap<String, usize> = HashMap::new();
        for edge in &edges {
            *degree.entry(edge.from.clone()).or_insert(0) += 1;
            *degree.entry(edge.to.clone()).or_insert(0) += 1;
        }
        let mut sorted: Vec<(usize, String)> = degree.into_iter().map(|(k, v)| (v, k)).collect();
        sorted.sort_by(|a, b| b.0.cmp(&a.0));

        let top_ids: std::collections::HashSet<String> = sorted.iter()
            .take(limit)
            .map(|(_, id)| id.clone())
            .collect();

        let filtered_nodes: Vec<Node> = nodes_map.into_iter()
            .filter(|(id, _)| top_ids.contains(id))
            .map(|(_, n)| n)
            .collect();

        let filtered_edges: Vec<Edge> = edges.into_iter()
            .filter(|e| top_ids.contains(&e.from) && top_ids.contains(&e.to))
            .collect();

        GraphData {
            total_nodes: filtered_nodes.len(),
            mode: "core".to_string(),
            nodes: filtered_nodes,
            edges: filtered_edges,
        }
    }

    pub fn get_status(&self) -> StatusData {
        let wiki_files: Vec<PathBuf> = walkdir(&self.wiki_dir, 1);
        let archived_files: Vec<PathBuf> = walkdir(&self.archived_dir, 3);

        let wiki_articles: Vec<String> = wiki_files.iter()
            .filter(|f| f.file_stem().map(|s| s != "index").unwrap_or(false))
            .map(|f| f.file_stem().unwrap().to_string_lossy().to_string())
            .collect();

        let archived_articles: Vec<String> = archived_files.iter()
            .filter(|f| f.file_stem().map(|s| s != "index").unwrap_or(false))
            .map(|f| f.file_stem().unwrap().to_string_lossy().to_string())
            .collect();

        let wiki_count = wiki_articles.len();
        let archived_count = archived_articles.len();

        let mut link_count = 0;
        let link_re = Regex::new(r"\[\[([^\]]+)\]\]").unwrap();
        for file in &wiki_files {
            let content = fs::read_to_string(file).unwrap_or_default();
            link_count += link_re.find_iter(&content).count();
        }

        let last_compile = wiki_files.last().and_then(|f| {
            fs::metadata(f).ok().map(|m| {
                let dt: DateTime<Local> = m.modified().unwrap().into();
                dt.format("%Y-%m-%d %H:%M:%S").to_string()
            })
        }).unwrap_or_else(|| "从未".to_string());

        StatusData {
            wiki_count,
            archived_count,
            total_count: wiki_count + archived_count,
            wiki_articles,
            archived_articles,
            link_count,
            last_compile,
            chroma_available: self.wiki_dir.parent().and_then(|p| p.parent()).map_or(false, |root| {
                root.join("storage/vector/chroma/chroma.sqlite3").exists()
            }),
        }
    }

    pub fn get_links(&self) -> Vec<LinkInfo> {
        let mut links = Vec::new();
        let link_re = Regex::new(r"\[\[([^\]]+)\]\]").unwrap();
        for file in walkdir(&self.wiki_dir, 1) {
            let stem = file.file_stem().unwrap().to_string_lossy().to_string();
            let content = fs::read_to_string(&file).unwrap_or_default();
            for cap in link_re.captures_iter(&content) {
                let target = cap[1].split('|').next().unwrap_or(&cap[1]).trim().to_string();
                links.push(LinkInfo { from: stem.clone(), to: target });
            }
        }
        links
    }
}

fn walkdir(dir: &Path, max_depth: usize) -> Vec<PathBuf> {
    if !dir.exists() { return vec![]; }
    walkdir::WalkDir::new(dir)
        .min_depth(1)
        .max_depth(max_depth)
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|p| p.path().extension().map_or(false, |ext| ext == "md"))
        .map(|p| p.path().to_path_buf())
        .collect()
}

fn extract_wikilinks(content: &str) -> Vec<String> {
    let re = Regex::new(r"\[\[([^\]]+)\]\]").unwrap();
    re.captures_iter(content).map(|c| c[1].to_string()).collect()
}

fn extract_summary(content: &str) -> String {
    content.lines()
        .find(|l| !l.trim().is_empty() && !l.starts_with('#'))
        .unwrap_or("")
        .trim()
        .to_string()
}

fn sorted_key(a: &str, b: &str) -> String {
    let mut v = vec![a.to_string(), b.to_string()];
    v.sort();
    v.join("::")
}
