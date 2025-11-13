# app.py (FULL CODE: Đã sửa lỗi khởi động và logic Min/Max Lùi)

from flask import Flask, request, jsonify, render_template
from docx import Document
from collections import deque 
import os
import re
from pyvis.network import Network
import webbrowser
import math

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
STATIC_FOLDER = os.path.join(os.getcwd(), 'static')
os.makedirs(STATIC_FOLDER, exist_ok=True)

@app.route("/")
def index():
    # return render_template("index.html")
    return render_template("thalassemia-diagnosis.html")


@app.route("/process_file", methods=["POST"])
def process_file():
    """
    Nhận file .docx, đọc nội dung, chuẩn hóa format.
    """
    if "file" not in request.files:
        return jsonify(success=False, message="Không có file nào được tải lên.")

    # Sửa lỗi: Gán 'file' ngay sau khi kiểm tra sự tồn tại
    file = request.files["file"]

    if not file.filename.endswith(".docx"):
        return jsonify(success=False, message="Chỉ chấp nhận file .docx.")

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        doc = Document(filepath)
        lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

        rules = [line for line in lines if "->" in line or "→" in line or "®" in line]
        GT, KL = "", ""
        notes = []

        for line in lines:
            if line.upper().startswith("GT"):
                GT = line.split("=")[-1].strip()
            elif line.upper().startswith("KL"):
                KL = line.split("=")[-1].strip()
            elif ":" in line and "->" not in line and "→" not in line and "®" not in line:
                notes.append(line.strip())

        formatted = ""
        for i, rule in enumerate(rules, 1):
            rule = rule.replace('Ù', '^').replace('®', '→')
            formatted += f"{i}. {rule}\n"

        formatted += "\n"
        formatted += f"GT = {GT}\n" if GT else ""
        formatted += f"KL = {KL}\n" if KL else ""
        if notes:
            formatted += "\nChú thích\n" + "\n".join(notes)

        return jsonify(success=True, formatted=formatted)

    except Exception as e:
        return jsonify(success=False, message=str(e))


# ----------------------------------------------------
# CÁC HÀM HỖ TRỢ SUY DIỄN (CHUNG)
# ----------------------------------------------------

def parse_content(content):
    """Phân tích nội dung chuẩn hóa thành rules, GT, KL."""
    rules = []
    GT = set()
    KL = set()
    
    cleaned_content = content.replace('Ù', '^').replace('®', '→')
    lines = cleaned_content.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        match = re.match(r"^(\d+)\.\s*(.*)", line)
        if match:
            try:
                idx = int(match.group(1).strip())
                rule_body = match.group(2).strip()
                
                if '→' in rule_body:
                    left_part, right_part = rule_body.split('→', 1)
                    left_facts = [f.strip() for f in left_part.split('^') if f.strip()]
                    right_fact = right_part.strip().split(',')[0].strip()
                    
                    if left_facts and right_fact:
                        rules.append((left_facts, right_fact, idx)) # Cấu trúc: (list, str, int)
            except:
                pass
                
        elif line.startswith("GT ="):
            facts_str = line.split("=", 1)[1].strip().strip('{}')
            GT = set(f.strip() for f in facts_str.split(',') if f.strip())

        elif line.startswith("KL ="):
            facts_str = line.split("=", 1)[1].strip().strip('{}')
            KL = set(f.strip() for f in facts_str.split(',') if f.strip())
            
    return rules, GT, KL


def LOC_all_applicable_rules(TG, R):
    """Tìm TẤT CẢ các luật thỏa mãn (vế trái thuộc TG và vế phải chưa có trong TG)"""
    applicable_rules = []
    for (left, right, idx) in R:
        if set(left).issubset(TG) and right not in TG:
            applicable_rules.append((left, right, idx))
    return applicable_rules

# ----------------------------------------------------
# LOGIC SUY DIỄN TIẾN - TẬP (Stack/Queue)
# ----------------------------------------------------

def forward_chaining(rules, GT, KL, mode="stack"):
    TG = set(GT)
    R = list(rules)
    VET = []
    history = []
    explanation = []
    
    THOA = deque() 
    
    history.append({"r": "", "THOA": "", "TG": ",".join(sorted(TG)),
                    "R": ",".join(str(r[2]) for r in R), "VET": ""})
    
    initial_thoa_rules = LOC_all_applicable_rules(TG, R)
    initial_thoa_rules_sorted = sorted(initial_thoa_rules, key=lambda x: x[2])

    if mode == "stack":
        THOA.extend(initial_thoa_rules_sorted) 
    else:
        THOA.extend(initial_thoa_rules_sorted)
    
    initial_thoa_indices = sorted([r[2] for r in THOA])
    history.append({"r": "", "THOA": ",".join(str(i) for i in initial_thoa_indices),
                    "TG": "", "R": "", "VET": ""})

    while THOA and not KL.issubset(TG):
        
        if mode == "stack":
            rule_to_apply = THOA.pop() 
        else:
            rule_to_apply = THOA.popleft() 
        
        left, right, idx = rule_to_apply
        
        TG.add(right)
        VET.append(str(idx)) 
        R = [r for r in R if r[2] != idx] 
        
        history.append({"r": str(idx), "THOA": "",
                        "TG": ",".join(sorted(TG)),
                        "R": ",".join(str(r[2]) for r in R) if R else "",
                        "VET": ",".join(VET)})
        
        left_str = " ^ ".join(left)
        explanation.append(f"Áp dụng luật {idx}: {left_str} → {right}. TG mới={{{', '.join(sorted(TG))}}}")

        if KL.issubset(TG):
            break
            
        current_THOA_indices = set(r[2] for r in THOA)
        all_applicable_rules = LOC_all_applicable_rules(TG, R)
        new_thoa_rules = [r for r in all_applicable_rules if r[2] not in current_THOA_indices]
        
        new_thoa_rules_sorted = sorted(new_thoa_rules, key=lambda x: x[2])
        if mode == "stack":
            THOA.extend(new_thoa_rules_sorted) 
        else:
            THOA.extend(new_thoa_rules_sorted)
            
        all_thoa_indices = sorted(list(current_THOA_indices.union(set(r[2] for r in new_thoa_rules))))
        
        history.append({"r": "", "THOA": ",".join(str(i) for i in all_thoa_indices) if all_thoa_indices else "",
                        "TG": "", "R": "", "VET": ""})

    proved = KL.issubset(TG)
    explanation.append("--------------------------------------------------")
    explanation.append("KL ⊆ TG, chứng minh thành công!" if proved else "❌ Kết thúc: Không suy được KL.")
    return history, proved, explanation

# ----------------------------------------------------
# LOGIC SUY DIỄN TIẾN - ĐỒ THỊ (FPG)
# ----------------------------------------------------

def build_graph_and_get_nodes(rules):
    """Xây dựng đồ thị logic FPG (Sự kiện) và trả về tất cả các node/cạnh."""
    graph = {}
    nodes = set()
    edges = []
    
    for left, head, idx in rules:
        nodes.add(head)
        nodes.update(left)
        
        for p in left:
            if p not in graph:
                graph[p] = []
            if head not in graph[p]:
                graph[p].append(head)
            
            edges.append((p, head, str(idx))) # LƯU CHỈ SỐ LUẬT DƯỚI DẠNG STR

    return graph, sorted(list(nodes)), edges


def shortest_distance(start, goal, graph):
    """Tính khoảng cách ngắn nhất giữa hai node (BFS)."""
    if start not in graph:
        return float("inf")

    if start == goal:
        return 0
        
    visited = {start}
    q = deque([(start, 0)])
    
    while q:
        node, dist = q.popleft()
        
        for nxt in graph.get(node, []):
            if nxt == goal:
                return dist + 1
            if nxt not in visited:
                visited.add(nxt)
                q.append((nxt, dist + 1))
    return float("inf")


def forward_chaining_fpg(rules, GT, KL, sub_opt):
    """Suy diễn tiến bằng phương pháp Đồ thị FPG (Heuristic khoảng cách)."""
    
    if not KL:
        return [], False, ["Lỗi: Không có Kết luận (KL) để suy diễn."], None
        
    try:
        goal = list(KL)[0]
    except (TypeError, IndexError):
        return [], False, ["Lỗi: Dữ liệu Kết luận không hợp lệ. Vui lòng kiểm tra format KL={...}."], None


    # LÀM SẠCH DANH SÁCH LUẬT 
    clean_rules = []
    for r in rules:
        if isinstance(r, tuple) and len(r) == 3:
            clean_rules.append(r)
        else:
             return [], False, [f"Lỗi cấu trúc luật: Expected tuple (left, head, idx) of length 3, found {type(r).__name__}: {r}"], None

    FPG_rules = {r[2]: (r[0], r[1]) for r in clean_rules} # Đảm bảo chỉ dùng rules sạch
    
    # 1. Xây dựng đồ thị logic FPG
    graph, all_nodes, all_edges = build_graph_and_get_nodes(clean_rules) 
    
    TG = set(GT)
    VET = [] 
    used_indices = set() 
    history = []
    explanation = []
    
    strategy = "MIN" if sub_opt == "min" else "MAX"
    explanation.append(f"----- Bắt đầu Suy diễn Tiến (FPG - {strategy}) -----")
    explanation.append(f"Giả thiết (GT): {', '.join(sorted(GT))}, Kết luận (KL): {goal}\n")
    
    # Khởi tạo bảng
    history.append({"r": "", "THOA": "", "TG": ",".join(sorted(TG)),
                    "R": ",".join(str(r[2]) for r in clean_rules), "VET": ""}) # Dùng clean_rules
    
    step = 1
    
    while goal not in TG:
        # 2. Tìm tất cả luật thỏa mãn và chưa được dùng
        THOA = []
        R_current_int = [] 
        for idx, (left, head) in FPG_rules.items():
            if idx not in used_indices:
                R_current_int.append(idx)
                if set(left).issubset(TG) and head not in TG:
                    THOA.append((idx, left, head))

        if not THOA:
            explanation.append("❌ Không còn luật nào thỏa mãn mà chưa suy ra KL.")
            break

        thoa_indices = sorted([r[0] for r in THOA])
        
        # 3. Tính Heuristic và chọn luật
        scored = []
        for idx, left, head in THOA:
            # KC = inf nếu không có đường đi. Max/Min cần xử lý inf/0 khác nhau.
            h_val = shortest_distance(head, goal, graph)
            scored.append((h_val, idx, head, left))
            
        # 🎯 LOGIC MAX/MIN HEURISTIC
        if sub_opt == "min":
            # Ưu tiên 1: Min KC. Ưu tiên 2: Min chỉ số
            scored.sort(key=lambda x: (x[0], x[1]))
        else: # sub_opt == "max"
            # Ưu tiên 1: Max KC. Ưu tiên 2: Min chỉ số
            scored.sort(key=lambda x: (-x[0] if x[0] != float('inf') else float('-inf'), x[1]))

        h_val, chosen_idx, head, left = scored[0]
        chosen = str(chosen_idx) # STR
        
        # 4. Áp dụng luật
        TG.add(head)
        VET.append(chosen) # STR
        used_indices.add(chosen_idx) # INT
        
        # Cập nhật Bảng (Dòng áp dụng luật)
        history.append({"r": chosen, "THOA": ",".join(str(i) for i in thoa_indices),
                        "TG": ",".join(sorted(TG)),
                        "R": ",".join(str(i) for i in sorted(R_current_int) if i != chosen_idx), 
                        "VET": ",".join(VET)}) 
        
        left_str = " ^ ".join(left)
        h_display = h_val if h_val != float('inf') else "inf"
        explanation.append(f"B{step}: h(r{chosen}) = KC({head}, {goal}) = {h_display}")
        explanation.append(f"-> Chọn luật {chosen} (h={h_display}) -> TG={{{','.join(sorted(TG))}}}")
        explanation.append(f"Áp dụng luật {chosen}: {left_str} → {head}. TG mới={{{', '.join(sorted(TG))}}}\n")

        step += 1

    proved = goal in TG
    explanation.append("--------------------------------------------------")
    explanation.append("✅ KL đạt được!" if proved else "❌ Không suy ra được KL.")

    # 5. Vẽ đồ thị và trả về tên file
    filename_relative = draw_fpg_interactive(GT, KL, all_nodes, all_edges, goal)
    
    return history, proved, explanation, filename_relative


# ----------------------------------------------------
# LOGIC SUY DIỄN TIẾN - ĐỒ THỊ (RPG)
# ----------------------------------------------------

def build_rpg(rules):
    """Xây dựng đồ thị logic RPG (Luật) và trả về các thành phần."""
    
    # rules_map: {idx: (left, head)}
    rules_map = {r[2]: (r[0], r[1]) for r in rules}
    
    rpg_graph = {idx: [] for idx in rules_map.keys()}
    
    # Xây dựng các cung ri -> rj
    for idx_i, (_, head_i) in rules_map.items():
        for idx_j, (left_j, _) in rules_map.items():
            # ri -> rj nếu Head(ri) là thành phần trong Left(rj)
            if head_i in left_j:
                rpg_graph[idx_i].append(idx_j)
                
    # Lấy danh sách các luật (node)
    all_rule_indices = sorted(rules_map.keys())
    
    return rpg_graph, all_rule_indices, rules_map


def shortest_distance_rpg(start_r_idx, goal_r_indices, rpg_graph):
    """Tính khoảng cách ngắn nhất từ luật start đến tập luật goal trên RPG."""
    
    # Chuyển goal_r_indices thành tập hợp để tra cứu nhanh
    goal_set = set(goal_r_indices)
    
    if start_r_idx in goal_set:
        return 0
        
    visited = {start_r_idx}
    q = deque([(start_r_idx, 0)])
    
    while q:
        r_idx, dist = q.popleft()
        
        for nxt_r_idx in rpg_graph.get(r_idx, []):
            if nxt_r_idx in goal_set:
                return dist + 1
            if nxt_r_idx not in visited:
                visited.add(nxt_r_idx)
                q.append((nxt_r_idx, dist + 1))
    return float("inf")


def forward_chaining_rpg(rules, GT, KL, sub_opt):
    """Suy diễn tiến bằng phương pháp Đồ thị RPG (Heuristic khoảng cách)."""
    
    # 1. Kiểm tra và làm sạch luật
    clean_rules = []
    for r in rules:
        if isinstance(r, tuple) and len(r) == 3:
            clean_rules.append(r)
        else:
             return [], False, [f"Lỗi cấu trúc luật: Expected tuple (left, head, idx) of length 3, found {type(r).__name__}: {r}"], None

    if not KL:
        return [], False, ["Lỗi: Không có Kết luận (KL) để suy diễn."], None

    try:
        goal = list(KL)[0]
    except (TypeError, IndexError):
        return [], False, ["Lỗi: Dữ liệu Kết luận không hợp lệ. Vui lòng kiểm tra format KL={...}."], None

    # 2. Xây dựng RPG và các tập luật đặc biệt
    # 🎯 SỬA LỖI: Giải nén biến all_r_indices từ build_rpg
    rpg_graph, all_r_indices, rules_map = build_rpg(clean_rules) 
    
    RGT_indices = [idx for idx, (left, _) in rules_map.items() if set(left).issubset(GT)] # Luật thỏa mãn GT
    RKL_indices = [idx for idx, (_, head) in rules_map.items() if head == goal]             # Luật sinh ra KL
    
    TG = set(GT)
    VET = [] 
    used_indices = set() 
    history = []
    explanation = []
    
    strategy = "MIN" if sub_opt == "min" else "MAX"
    explanation.append(f"----- Bắt đầu Suy diễn Tiến (RPG - {strategy}) -----")
    explanation.append(f"Giả thiết (GT): {', '.join(sorted(GT))}, Kết luận (KL): {goal}\n")
    
    # Khởi tạo bảng
    history.append({"r": "", "THOA": "", "TG": ",".join(sorted(TG)),
                    "R": ",".join(str(r[2]) for r in clean_rules), "VET": ""})
    
    step = 1
    
    while goal not in TG:
        # 3. Tìm THOA và R_current
        THOA = []
        R_current_int = [] 
        for idx, (left, head) in rules_map.items():
            if idx not in used_indices:
                R_current_int.append(idx)
                if set(left).issubset(TG) and head not in TG:
                    THOA.append((idx, left, head))

        if not THOA:
            explanation.append("❌ Không còn luật nào thỏa mãn mà chưa suy ra KL.")
            break

        thoa_indices = sorted([r[0] for r in THOA])
        
        # 4. Tính Heuristic và chọn luật (Min/Max KC đến RKL, Min chỉ số)
        scored = []
        for idx, left, head in THOA:
            # Tính h(r) = KC(r, RKL)
            h_val = shortest_distance_rpg(idx, RKL_indices, rpg_graph)
            scored.append((h_val, idx, head, left))

        # 🎯 LOGIC MAX/MIN HEURISTIC
        if sub_opt == "min":
            # Ưu tiên 1: Min KC. Ưu tiên 2: Min chỉ số
            scored.sort(key=lambda x: (x[0], x[1]))
        else: # sub_opt == "max"
            # Ưu tiên 1: Max KC. Ưu tiên 2: Min chỉ số
            scored.sort(key=lambda x: (-x[0] if x[0] != float('inf') else float('-inf'), x[1]))

        h_val, chosen_idx, head, left = scored[0]
        chosen = str(chosen_idx) # STR
        
        # 5. Áp dụng luật
        TG.add(head)
        VET.append(chosen) 
        used_indices.add(chosen_idx) 
        
        # Cập nhật Bảng
        history.append({"r": chosen, "THOA": ",".join(str(i) for i in thoa_indices),
                        "TG": ",".join(sorted(TG)),
                        "R": ",".join(str(i) for i in sorted(R_current_int) if i != chosen_idx), 
                        "VET": ",".join(VET)}) 
        
        left_str = " ^ ".join(left)
        h_display = h_val if h_val != float('inf') else "inf"
        explanation.append(f"B{step}: h(r{chosen}) = KC(r{chosen}, RKL) = {h_display}")
        explanation.append(f"-> Chọn luật {chosen} (h={h_display}) -> TG={{{','.join(sorted(TG))}}}")
        explanation.append(f"Áp dụng luật {chosen}: {left_str} → {head}. TG mới={{{', '.join(sorted(TG))}}}\n")

        step += 1

    proved = goal in TG
    explanation.append("--------------------------------------------------")
    explanation.append("✅ KL đạt được!" if proved else "❌ Không suy ra được KL.")

    # 6. Vẽ đồ thị RPG
    filename_relative = draw_rpg_interactive(clean_rules, RGT_indices, RKL_indices, goal, all_r_indices, rpg_graph)
    
    return history, proved, explanation, filename_relative


def draw_rpg_interactive(rules, RGT_indices, RKL_indices, goal, nodes, graph, filename_prefix="rpg"):
    """Vẽ đồ thị RPG tương tác (Đỉnh là luật)."""
    
    unique_id = os.getpid()
    filename_html = f"{filename_prefix}_{unique_id}.html"
    filepath_abs = os.path.join(STATIC_FOLDER, filename_html)
    
    net = Network(height="650px", width="95%", directed=True) 
    net.toggle_physics(False)

    net.set_options("""
    {
      "nodes": { "scaling": { "min": 30, "max": 30 }, "font": { "size": 30, "align": "center" } },
      "edges": { "smooth": false }
    }
    """)

    # Định vị node
    R_radius = 350
    rules_map = {r[2]: (r[0], r[1]) for r in rules}

    for i, idx in enumerate(nodes):
        # Nội dung luật
        left, head = rules_map[idx]
        label = f"r{idx}"
        title = f"r{idx}: {', '.join(left)} -> {head}"
        
        angle = 2 * math.pi * i / len(nodes)
        x = R_radius * math.cos(angle)
        y = R_radius * math.sin(angle)

        # Xác định màu: Vàng (KL), Đỏ (GT), Xanh (Khác)
        if idx in RKL_indices:
            color = "#ffeb3b" # Yellow (KL)
        elif idx in RGT_indices:
            color = "#f44336" # Red (GT)
        else:
            color = "#03a9f4" # Light Blue

        net.add_node(
            idx, label=label, title=title, color=color,
            shape="circle", value=30,
            physics=False, fixed=False, x=x, y=y 
        )

    # Thêm cạnh
    for u_idx, targets in graph.items():
        for v_idx in targets:
            net.add_edge(u_idx, v_idx, arrows="to", color="gray", smooth=False)

    net.write_html(filepath_abs)
    
    return f"static/{filename_html}" 


def draw_fpg_interactive(gt, kl, nodes, edges, goal, filename_prefix="fpg"):
    """Vẽ đồ thị FPG tương tác và lưu vào thư mục static."""
    
    unique_id = os.getpid()
    filename_html = f"{filename_prefix}_{unique_id}.html"
    
    filepath_abs = os.path.join(STATIC_FOLDER, filename_html)
    
    net = Network(height="650px", width="95%", directed=True) 
    net.toggle_physics(False)

    net.set_options("""
    {
      "nodes": { "scaling": { "min": 30, "max": 30 }, "font": { "size": 30, "align": "center" } },
      "edges": { "smooth": false }
    }
    """)

    R_radius = 350
    for i, n in enumerate(nodes):
        angle = 2 * math.pi * i / len(nodes)
        x = R_radius * math.cos(angle)
        y = R_radius * math.sin(angle)

        if n == goal:
            color = "#ffeb3b"
        elif n in gt:
            color = "#f44336"
        else:
            color = "#03a9f4"

        net.add_node(
            n, label=n, color=color,
            shape="circle", value=30,
            physics=False, fixed=False, x=x, y=y 
        )

    for u, v, label in edges:
        net.add_edge(u, v, title=f"r{label}", arrows="to", color="gray", smooth=False)

    net.write_html(filepath_abs)
    
    return f"static/{filename_html}" 


# ----------------------------------------------------
# LOGIC SUY DIỄN LÙI (BACKWARD CHAINING)
# ----------------------------------------------------

class Node:
    def __init__(self, goals, parent=None, rule_used=None, goal_proven=None):
        self.goals = frozenset(goals) # Tập goals hiện tại (immutable)
        self.parent = parent
        self.rule_used = rule_used   # Chỉ số luật (int)
        self.goal_proven = goal_proven # Mục tiêu (str)
        self.children = []
        self.is_terminal = False
        self.is_success = False

def draw_backward_graph(root_node, GT, KL, filename_prefix="backward"):
    """Vẽ toàn bộ cây suy diễn lùi (Search Tree) bằng pyvis mà không gộp node."""
    
    unique_id = os.getpid()
    filename_html = f"{filename_prefix}_{unique_id}.html"
    filepath_abs = os.path.join(STATIC_FOLDER, filename_html)
    
    net = Network(height="650px", width="95%", directed=True) 
    net.toggle_physics(False)
    
    # Cấu hình đồ thị dạng cây ngang
    net.set_options("""{"layout": {"hierarchical": {"enabled": true, "direction": "LR", "sortMethod": "directed", "levelSeparation": 150}}}""")

    node_counter = 0 
    
    def add_node_recursive(node, parent_id=None):
        nonlocal node_counter
        
        # 🎯 SỬA: Luôn tạo ID mới cho mỗi node trong cây (đây là ID vẽ)
        node_id_label = f"N_{node_counter}"
        node_counter += 1
        
        # 1. Định nghĩa Node
        goals_label = "{" + ", ".join(sorted(node.goals)) + "}"
        
        # Màu sắc
        if node.goals.issubset(GT) and node.goals:
            color = "#4CAF50" # Green (Thành công - Đã chứng minh)
        elif node.parent is None:
            color = "#ffeb3b" # Yellow (KL Gốc)
        else:
            color = "#03a9f4" # Blue (Mục tiêu trung gian)
            
        
        title_text = f"Mục tiêu: {goals_label}"
        if node.rule_used:
             title_text += f"\nLuật áp dụng: r{node.rule_used}"
        
        net.add_node(node_id_label, label=goals_label, title=title_text, color=color, shape="box", fixed=True)
        
        # 2. Định nghĩa Cạnh
        if parent_id is not None:
            rule_label = f"r{node.rule_used}"
            
            # 🎯 LƯU Ý: Không phân biệt Chu trình nữa, chỉ vẽ cung
            net.add_edge(parent_id, node_id_label, label=rule_label, title=rule_label, color="#000000", arrows="to")

        # 3. Đệ quy cho các nhánh con
        for child in node.children:
            add_node_recursive(child, node_id_label)
            
        return node_id_label

    add_node_recursive(root_node)
    
    net.write_html(filepath_abs)
    
    return f"static/{filename_html}"


def find_backward_tree(rules_map, start_goals, GT, sub_opt):
    """Tạo cây suy diễn lùi (Search Tree) và trả về node gốc."""
    
    start_node = Node(goals=start_goals)
    stack = [start_node] 
    visited_goals = {start_node.goals} 
    
    found_path = None 
    
    # 1. Xử lý chiến lược Min/Max (Áp dụng cho việc SẮP XẾP luật)
    def sort_rules(rules_to_score, sub_opt):
        # rules_to_score: List of (idx, left, head)
        if sub_opt == "min":
            # 🎯 SỬA: Sắp xếp DESC (Max key) để luật MIN (r10) được pop TRƯỚC
            return sorted(rules_to_score, key=lambda x: x[0], reverse=True) 
        else: # sub_opt == "max"
            # 🎯 SỬA: Sắp xếp ASC (Min key) để luật MAX (r16) được pop TRƯỚC
            return sorted(rules_to_score, key=lambda x: x[0]) 

    while stack and found_path is None:
        current = stack.pop()
        
        # Điều kiện dừng thành công
        if current.goals.issubset(GT):
            current.is_terminal = True
            current.is_success = True
            # Thu thập vết thành công ngay khi tìm thấy (Vết đầu tiên theo thứ tự ưu tiên)
            path = []
            temp = current
            while temp is not None:
                path.append(temp)
                temp = temp.parent
            found_path = path[::-1] # Đảo ngược path (Root -> Leaf)
            continue
        
        goals_to_prove = sorted(list(current.goals - GT)) 

        if not goals_to_prove:
            current.is_terminal = True
            current.is_success = False
            continue

        # Chỉ giải quyết mục tiêu đầu tiên (DFS-like)
        goal_to_prove = goals_to_prove[0] 
        
        # Tìm tất cả các luật có thể suy ra mục tiêu này
        applicable_rules = [
            (idx, left, head) for idx, (left, head) in rules_map.items() 
            if head == goal_to_prove
        ]
        
        # 3. Áp dụng chiến lược Min/Max để SẮP XẾP thứ tự rẽ nhánh
        sorted_applicable_rules = sort_rules(applicable_rules, sub_opt)
        
        if not sorted_applicable_rules:
            current.is_terminal = True
            current.is_success = False
            continue

        # 4. Rẽ nhánh theo thứ tự đã sắp xếp (Đảo ngược để pop theo thứ tự ưu tiên)
        sorted_applicable_rules.reverse() 
        
        for idx, left, head in sorted_applicable_rules:
            r_name = idx
            
            # Mục tiêu mới (thêm left, bỏ head)
            new_goals_set = (current.goals - {goal_to_prove}) | set(left)
            
            # Kiểm tra vòng lặp
            is_cycle = new_goals_set in visited_goals 
            
            # Tạo node mới (dù là chu trình hay không)
            new_node = Node(goals=new_goals_set, parent=current, rule_used=r_name, goal_proven=goal_to_prove)
            current.children.append(new_node)
            
            if is_cycle:
                new_node.is_terminal = True
                new_node.is_success = False
            else:
                # Nếu không phải chu trình, thăm và thêm vào stack
                visited_goals.add(new_goals_set)
                stack.append(new_node) 

    return start_node, found_path


def collect_successful_paths(root_node):
    """Hàm này không còn cần thiết vì find_backward_tree đã trả về vết."""
    pass


def backward_chaining(rules, GT, KL, sub_opt):
    """Suy diễn lùi, tạo cây, và chọn vết Min/Max."""
    
    if not KL:
        return [], False, ["Lỗi: Không có Kết luận (KL) để suy diễn."], None

    try:
        goal = list(KL)[0]
    except (TypeError, IndexError):
        return [], False, ["Lỗi: Dữ liệu Kết luận không hợp lệ. Vui lòng kiểm tra format KL={...}."], None

    # LÀM SẠCH DANH SÁCH LUẬT 
    clean_rules = []
    for r in rules:
        if isinstance(r, tuple) and len(r) == 3:
            clean_rules.append(r)
        else:
             return [], False, [f"Lỗi cấu trúc luật: Expected tuple (left, head, idx) of length 3, found {type(r).__name__}: {r}"], None

    rules_map = {r[2]: (r[0], r[1]) for r in clean_rules} # {idx: (left, head)}
    
    # 1. Tạo cây tìm kiếm và tìm vết đầu tiên
    root_node, chosen_path = find_backward_tree(rules_map, KL, GT, sub_opt)
    
    explanation = []
    explanation.append(f"----- Bắt đầu Suy diễn Lùi ({sub_opt.upper()}) -----")
    explanation.append(f"Giả thiết (GT): {', '.join(sorted(GT))}, Kết luận (KL): {goal}\n")
    
    if chosen_path is None:
        explanation.append("❌ Không tìm thấy vết suy diễn hợp lệ nào từ KL đến GT.")
        return [], False, explanation, None

    # 4. Xây dựng Lời giải và Đồ thị
    num_rules_applied = len(chosen_path) - 1 # Root node không tính
    explanation.append(f"✅ Vết được chọn (Độ dài {num_rules_applied} luật):")
    
    final_vet = []
    
    # Sửa lỗi Lời giải: Bắt đầu từ node thứ hai (luật đầu tiên được áp dụng)
    for i, node in enumerate(chosen_path[1:]): 
        r_name = str(node.rule_used)
        r_head = node.goal_proven
        
        final_vet.append(r_name)
        
        explanation.append(f"{i+1}. Áp dụng r{r_name} (chứng minh {r_head}): Mục tiêu mới = {{{', '.join(sorted(node.goals))}}}")
        
    explanation.append("--------------------------------------------------")
    explanation.append(f"VET = {{{', '.join(final_vet)}}}")
    
    # 5. Vẽ đồ thị
    graph_file = draw_backward_graph(root_node, GT, KL)
    
    return [], True, explanation, graph_file


def draw_fpg_interactive(gt, kl, nodes, edges, goal, filename_prefix="fpg"):
    """Vẽ đồ thị FPG tương tác và lưu vào thư mục static."""
    
    unique_id = os.getpid()
    filename_html = f"{filename_prefix}_{unique_id}.html"
    
    filepath_abs = os.path.join(STATIC_FOLDER, filename_html)
    
    net = Network(height="650px", width="95%", directed=True) 
    net.toggle_physics(False)

    net.set_options("""
    {
      "nodes": { "scaling": { "min": 30, "max": 30 }, "font": { "size": 30, "align": "center" } },
      "edges": { "smooth": false }
    }
    """)

    R_radius = 350
    for i, n in enumerate(nodes):
        angle = 2 * math.pi * i / len(nodes)
        x = R_radius * math.cos(angle)
        y = R_radius * math.sin(angle)

        if n == goal:
            color = "#ffeb3b"
        elif n in gt:
            color = "#f44336"
        else:
            color = "#03a9f4"

        net.add_node(
            n, label=n, color=color,
            shape="circle", value=30,
            physics=False, fixed=False, x=x, y=y 
        )

    for u, v, label in edges:
        net.add_edge(u, v, title=f"r{label}", arrows="to", color="gray", smooth=False)

    net.write_html(filepath_abs)
    
    return f"static/{filename_html}" 


def draw_rpg_interactive(rules, RGT_indices, RKL_indices, goal, nodes, graph, filename_prefix="rpg"):
    """Vẽ đồ thị RPG tương tác (Đỉnh là luật)."""
    
    unique_id = os.getpid()
    filename_html = f"{filename_prefix}_{unique_id}.html"
    filepath_abs = os.path.join(STATIC_FOLDER, filename_html)
    
    net = Network(height="650px", width="95%", directed=True) 
    net.toggle_physics(False)

    net.set_options("""
    {
      "nodes": { "scaling": { "min": 30, "max": 30 }, "font": { "size": 30, "align": "center" } },
      "edges": { "smooth": false }
    }
    """)

    # Định vị node
    R_radius = 350
    rules_map = {r[2]: (r[0], r[1]) for r in rules}

    for i, idx in enumerate(nodes):
        # Nội dung luật
        left, head = rules_map[idx]
        label = f"r{idx}"
        title = f"r{idx}: {', '.join(left)} -> {head}"
        
        angle = 2 * math.pi * i / len(nodes)
        x = R_radius * math.cos(angle)
        y = R_radius * math.sin(angle)

        # Xác định màu: Vàng (KL), Đỏ (GT), Xanh (Khác)
        if idx in RKL_indices:
            color = "#ffeb3b" # Yellow (KL)
        elif idx in RGT_indices:
            color = "#f44336" # Red (GT)
        else:
            color = "#03a9f4" # Light Blue

        net.add_node(
            idx, label=label, title=title, color=color,
            shape="circle", value=30,
            physics=False, fixed=False, x=x, y=y 
        )

    # Thêm cạnh
    for u_idx, targets in graph.items():
        for v_idx in targets:
            net.add_edge(u_idx, v_idx, arrows="to", color="gray", smooth=False)

    net.write_html(filepath_abs)
    
    return f"static/{filename_html}" 


@app.route("/execute_forward", methods=["POST"])
def execute_forward():
    """
    Thực hiện suy diễn (Tiến/Lùi) dựa trên dữ liệu người dùng gửi.
    """
    try:
        data = request.json
        content = data.get("content")
        sub_opt = data.get("subOpt", "Stack").lower() 
        main_opt = data.get("mainOpt", "Tập").lower()
        graph_type = data.get("graphOpt", None)
        
        if not content:
             return jsonify(success=False, message="Nội dung suy diễn trống.")

        rules, GT, KL = parse_content(content)
        
        if not GT or not KL:
            return jsonify(success=False, message=f"Lỗi: Không tìm thấy GT/KL. Vui lòng kiểm tra format 'GT = {{...}}' và 'KL = {{...}}' trong nội dung đã chuẩn hóa.")
        if not rules:
             return jsonify(success=False, message=f"Không tìm thấy luật trong nội dung.")

        graph_file = None
        
        if main_opt == "tập":
            history, proved, explanation = forward_chaining(rules, GT, KL, mode=sub_opt)
            graph_file = None
        elif main_opt == "đồ thị":
            if graph_type == "fpg":
                 history, proved, explanation, graph_file = forward_chaining_fpg(rules, GT, KL, sub_opt)
            elif graph_type == "rpg":
                 history, proved, explanation, graph_file = forward_chaining_rpg(rules, GT, KL, sub_opt)
            else:
                 return jsonify(success=False, message=f"Lỗi: Loại đồ thị {graph_type.upper()} không hợp lệ.")
        elif main_opt == "lùi": # Xử lý Suy diễn Lùi
             # Suy diễn lùi không cần history (bảng)
             history, proved, explanation, graph_file = backward_chaining(rules, GT, KL, sub_opt)
        else:
             return jsonify(success=False, message=f"Chế độ {main_opt.upper()} chưa được hỗ trợ.")

        # Trả về tên file đồ thị (nếu có)
        return jsonify(success=True, history=history, explanation=explanation, proved=proved, graph_file=graph_file)

    except Exception as e:
        # DEBUG: Trả về lỗi chi tiết từ Python thay vì lỗi chung
        return jsonify(success=False, message=f"Lỗi hệ thống: {type(e).__name__}: {str(e)}")


if __name__ == "__main__":
    app.run(debug=True)