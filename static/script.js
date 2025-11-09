// script.js (FULL CODE: Đã loại bỏ tùy chọn "Chỉ số" chính và tích hợp logic Lùi)

const btnTien = document.getElementById("btnTien");
const btnLui = document.getElementById("btnLui");
const optionsDiv = document.getElementById("options");
const subOptionsDiv = document.getElementById("subOptions");
const helpBtn = document.getElementById("helpBtn");
const helpPopup = document.getElementById("helpPopup");
const closeHelp = document.getElementById("closeHelp");
const executeBtn = document.querySelector(".execute-btn");
const leftCol = document.querySelector(".left-col");
const rightCol = document.querySelector(".right-col");

const fileInfo = document.getElementById("fileInfo");
const fileName = document.getElementById("fileName");
const editBtn = document.getElementById("editBtn");
const deleteBtn = document.getElementById("deleteBtn");
const uploadBtn = document.querySelector(".upload-btn");
const fileInput = document.getElementById("fileInput");

let mode = "tien"; // tiến mặc định
let fileDialogOpen = false; // chống double-click

// Khi thay đổi chế độ Tiến / Lùi
btnTien.addEventListener("click", () => {
    mode = "tien";
    btnTien.classList.add("active");
    btnLui.classList.remove("active");
    renderOptions();
});

btnLui.addEventListener("click", () => {
    mode = "lui";
    btnLui.classList.add("active");
    btnTien.classList.remove("active");
    renderOptions();
});

// Render các lựa chọn chính theo chế độ (CHỈ CÒN TẬP/ĐỒ THỊ/LÙI)
function renderOptions() {
    optionsDiv.innerHTML = "";
    subOptionsDiv.innerHTML = ""; 

    // 🎯 Sửa: CHỈ CÒN TẬP VÀ ĐỒ THỊ (TIẾN) HOẶC LÙI
    const mainOpts = mode === "tien" ? ["Tập", "Đồ thị"] : ["Lùi"];
    
    // Thêm các lựa chọn chính
    mainOpts.forEach(o => {
        const label = document.createElement("label");
        label.innerHTML = `<input type="radio" name="mainOpt" value="${o.toLowerCase()}"> ${o}`;
        optionsDiv.appendChild(label);
    });

    // Thiết lập trình nghe sự kiện cho lựa chọn chính
    optionsDiv.querySelectorAll("input").forEach(radio => {
        radio.addEventListener("change", (e) => showSubOptions(e.target.value));
    });
    
    // Tự động chọn tùy chọn đầu tiên (Tập hoặc Lùi)
    const firstOpt = optionsDiv.querySelector('input[name="mainOpt"]');
    if (firstOpt) {
        firstOpt.checked = true;
        showSubOptions(firstOpt.value);
    }
}

// Hàm ban đầu: Hiển thị các tùy chọn phụ dựa trên lựa chọn chính
function showSubOptions(selected) {
    subOptionsDiv.innerHTML = "";

    let subs = [];
    let subGroupName = "";
    
    if (selected === "tập") {
        // --- Nhóm Tập (Stack/Queue) ---
        subGroupName = "setOpt"; 
        subs = ["Stack", "Queue"];
        
        subs.forEach(s => {
            const label = document.createElement("label");
            label.innerHTML = `<input type="radio" name="${subGroupName}" value="${s.toLowerCase()}"> ${s}`;
            subOptionsDiv.appendChild(label);
        });
        
        // Tự động chọn Stack
        const firstSubOpt = subOptionsDiv.querySelector(`input[name="${subGroupName}"]`);
        if (firstSubOpt) {
            firstSubOpt.checked = true;
        }

    } else if (selected === "đồ thị") {
        
        // --- Nhóm 1: Loại Đồ thị (graphTypeOpt) ---
        const graphDiv = document.createElement("div");
        graphDiv.innerHTML = "<h4>Chọn loại Đồ thị:</h4>";
        const graphOpts = mode === "tien" ? ["FPG", "RPG"] : ["FPG"];
        
        graphOpts.forEach(s => {
            const label = document.createElement("label");
            label.innerHTML = `<input type="radio" name="graphTypeOpt" value="${s.toLowerCase()}"> ${s}`;
            graphDiv.appendChild(label);
        });
        subOptionsDiv.appendChild(graphDiv);
        
        // --- Nhóm 2: Heuristic (Min/Max) ---
        subOptionsDiv.innerHTML += "<hr style='width: 80%; border-top: 1px solid #e0e0e0; margin: 10px 0;'>";
        const heuristicDiv = document.createElement("div");
        heuristicDiv.innerHTML = "<h4>Chỉ số:</h4>";
        const h_subs = ["Min", "Max"];
        
        h_subs.forEach(s => {
            const label = document.createElement("label");
            label.innerHTML = `<input type="radio" name="heuristicOpt" value="${s.toLowerCase()}"> ${s}`;
            heuristicDiv.appendChild(label);
        });
        subOptionsDiv.appendChild(heuristicDiv);
        
        
        // Tự động chọn FPG và Min
        graphDiv.querySelector('input[name="graphTypeOpt"]').checked = true;
        heuristicDiv.querySelector('input[name="heuristicOpt"]').checked = true;
        
    } else if (selected === "lùi") { // 🎯 Suy diễn Lùi (Chỉ có Min/Max)
        
        // --- Nhóm 1: Heuristic (Min/Max) ---
        const heuristicDiv = document.createElement("div");
        heuristicDiv.innerHTML = "<h4>Chỉ số:</h4>";
        const h_subs = ["Min", "Max"]; // Độ dài vết min/max
        
        h_subs.forEach(s => {
            const label = document.createElement("label");
            label.innerHTML = `<input type="radio" name="heuristicOpt" value="${s.toLowerCase()}"> ${s}`;
            heuristicDiv.appendChild(label);
        });
        subOptionsDiv.appendChild(heuristicDiv);
        
        // Tự động chọn Min
        heuristicDiv.querySelector('input[name="heuristicOpt"]').checked = true;
    }
}


// Hàm phụ trợ: Không cần updateSubOptionsState phức tạp nữa
function updateSubOptionsState() {
    // Logic đã được gộp vào showSubOptions
}


// Hiển thị popup hướng dẫn
helpBtn.addEventListener("click", () => {
    helpPopup.style.display = "flex";
});

closeHelp.addEventListener("click", () => {
    helpPopup.style.display = "none";
});

// Khởi tạo ban đầu
renderOptions();

// ------------------- (Phần Upload File Giữ Nguyên) -------------------

// Khi nhấn "Nhập dữ liệu"
uploadBtn.addEventListener("click", () => {
    if (!fileDialogOpen) {
        fileDialogOpen = true;
        fileInput.click();
    }
});

// Khi chọn hoặc hủy chọn file
fileInput.addEventListener("change", (e) => {
    fileDialogOpen = false; // reset cờ
    const file = e.target.files[0];
    if (!file) return;

    let shortName = file.name;
    if (shortName.length > 20) shortName = shortName.slice(0, 17) + "...";
    fileName.textContent = shortName;

    uploadBtn.style.display = "none";
    fileInfo.style.display = "block";

    // 🔹 Gửi file lên Flask để xử lý và lấy nội dung chuẩn hóa
    const formData = new FormData();
    formData.append("file", file);

    fetch("/process_file", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            window.formattedText = data.formatted;
        } else {
            alert("Lỗi xử lý file: " + data.message);
        }
    })
    .catch(err => {
        alert("Không thể kết nối server.");
        console.error(err);
    });
});

// Nút "Sửa" → hiển thị nội dung đã chuẩn hóa
editBtn.addEventListener("click", () => {
    if (!window.formattedText) {
        alert("Chưa có nội dung để sửa. Hãy chọn lại file .docx.");
        return;
    }

    // Tạo khung chỉnh sửa
    const editor = document.createElement("div");
    editor.className = "editor-popup";
    editor.innerHTML = `
        <div class="editor-box">
            <h3>Nội dung file đã chuẩn hóa</h3>
            <textarea id="editArea">${window.formattedText}</textarea>
            <div class="editor-actions">
                <button id="resetEdit">Reset</button>
                <button id="backEdit">Trở về</button>
            </div>
        </div>
    `;
    document.body.appendChild(editor);

    // Lấy phần tử
    const editArea = document.getElementById("editArea");
    const resetBtn = document.getElementById("resetEdit");
    const backBtn = document.getElementById("backEdit");

    // Nút Reset → xóa nội dung
    resetBtn.addEventListener("click", () => {
        editArea.value = "";
    });

    // Nút Trở về → lưu lại nội dung đã chỉnh và đóng popup
    backBtn.addEventListener("click", () => {
        window.formattedText = editArea.value;
        editor.remove();
    });
});

// Nút "Xóa" → reset lại giao diện
deleteBtn.addEventListener("click", () => {
    fileInput.value = "";
    fileInfo.style.display = "none";
    uploadBtn.style.display = "inline-block";
    fileDialogOpen = false;
    window.formattedText = "";
});


// ----------------------------------------------------
// LOGIC XỬ LÝ NÚT "THỰC HIỆN" (EXECUTE)
// ----------------------------------------------------

// Hàm để lấy dữ liệu tùy chọn hiện tại
function getSelectedOptions() {
    const mainOpt = document.querySelector('input[name="mainOpt"]:checked')?.value;
    
    let setOptValue = null; // Stack/Queue
    let heuristicOptValue = null; // Min/Max
    let graphTypeOptValue = null; // FPG/RPG

    if (mainOpt === "tập") {
        setOptValue = document.querySelector('input[name="setOpt"]:checked')?.value;
    } else if (mainOpt === "đồ thị" || mainOpt === "lùi") { 
        heuristicOptValue = document.querySelector('input[name="heuristicOpt"]:checked')?.value; // Min/Max
        if (mainOpt === "đồ thị") {
            graphTypeOptValue = document.querySelector('input[name="graphTypeOpt"]:checked')?.value; // FPG/RPG
        }
    }

    // Trả về Heuristic nếu là Đồ thị/Lùi, nếu không thì là Stack/Queue
    const subOptValue = heuristicOptValue || setOptValue; 

    return { mainOpt: mainOpt, subOpt: subOptValue, graphTypeOpt: graphTypeOptValue };
}


executeBtn.addEventListener("click", () => {
    if (!window.formattedText) {
        alert("Vui lòng nhập dữ liệu trước khi thực hiện.");
        return;
    }

    const { mainOpt, subOpt, graphTypeOpt } = getSelectedOptions();

    // 1. Kiểm tra tính hợp lệ của chế độ và tùy chọn
    let isSupported = false;
    let finalSubOpt = subOpt; 
    let selectedSubOptLabel = "";

    if (!mainOpt || !finalSubOpt) {
        alert("Vui lòng chọn Tùy chọn chính và Tùy chọn phụ.");
        return;
    }
    
    if (mode === "tien") {
        if (mainOpt === "tập") {
            isSupported = (finalSubOpt === "stack" || finalSubOpt === "queue");
            selectedSubOptLabel = finalSubOpt.toUpperCase();
        } else if (mainOpt === "đồ thị") {
            if (!graphTypeOpt) {
                 alert("Vui lòng chọn loại Đồ thị (FPG/RPG).");
                 return;
            }
            isSupported = (finalSubOpt === "min" || finalSubOpt === "max") && (graphTypeOpt === "fpg" || graphTypeOpt === "rpg");
            selectedSubOptLabel = `${graphTypeOpt.toUpperCase()} (${finalSubOpt.toUpperCase()})`;
        } 
    } else if (mode === "lui") { // 🎯 Kiểm tra Lùi
         if (mainOpt === "lùi") {
             isSupported = (finalSubOpt === "min" || finalSubOpt === "max");
             selectedSubOptLabel = `LÙI (${finalSubOpt.toUpperCase()})`;
         }
    }
    
    if (!isSupported) {
        alert(`Chế độ ${mode.toUpperCase()} - ${mainOpt.toUpperCase()} - ${finalSubOpt.toUpperCase()} hiện chưa được hỗ trợ.`);
        return;
    }

    // 2. Gửi yêu cầu chạy suy diễn
    const requestData = {
        mode: mode,
        mainOpt: mainOpt,
        subOpt: finalSubOpt, // Stack/Queue hoặc Min/Max
        graphOpt: graphTypeOpt, // FPG/RPG (null nếu là chế độ Tập/Lùi)
        content: window.formattedText
    };

    fetch("/execute_forward", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(requestData)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            displayResults(data.history, data.explanation, data.proved, data.graph_file, mainOpt, selectedSubOptLabel); 
        } else {
            alert("Lỗi thực hiện: " + data.message);
        }
    })
    .catch(err => {
        alert("Không thể kết nối server để chạy suy diễn.");
        console.error(err);
    });
});

// Hàm hiển thị kết quả (Lời Giải và Bảng/Đồ thị)
function displayResults(history, explanation, proved, graphFile = null, mainOpt, selectedSubOptLabel) {
    
    // 1. Hiển thị Lời Giải (Luôn luôn)
    leftCol.innerHTML = `<h3>Lời Giải ${proved ? "✅" : "❌"}</h3>`;
    const explanationDiv = document.createElement("div");

    explanationDiv.className = "explanation-log"; 
    explanationDiv.style.maxHeight = "calc(100vh - 80px)"; 
    explanationDiv.style.overflowY = "auto";

    explanation.forEach(line => {
        const p = document.createElement("p");
        p.textContent = line;
        explanationDiv.appendChild(p);
    });
    leftCol.appendChild(explanationDiv);


    // 2. Hiển thị Bảng HOẶC Đồ Thị
    rightCol.innerHTML = `<h3>Bảng hoặc Đồ Thị (${selectedSubOptLabel})</h3>`;
    
    // NẾU LÀ CHẾ ĐỘ ĐỒ THỊ (FPG/RPG/LÙI): Hiển thị IFRAME
    if (mainOpt === "đồ thị" || mainOpt === "lùi") {
        
        // Sửa lỗi: Cần reset overflow của rightCol để iframe hiển thị full
        rightCol.style.overflowY = "hidden";
        
        if (graphFile) {
             // NEW: Nhúng đồ thị vào iframe
            const iframe = document.createElement("iframe");
            iframe.src = graphFile; // Sử dụng đường dẫn từ Flask
            iframe.style.width = "100%";
            iframe.style.height = "calc(100vh - 100px)"; // Đủ cao để hiển thị
            iframe.style.border = "none";
            
            rightCol.appendChild(iframe);
        } else {
            const messageDiv = document.createElement("div");
            messageDiv.style.padding = "20px";
            messageDiv.style.textAlign = "center";
            messageDiv.innerHTML = "<p style='color: red; font-weight: bold;'>Lỗi: Không tạo được file đồ thị.</p>";
            rightCol.appendChild(messageDiv);
        }
        
        return; // Kết thúc hàm nếu là Đồ thị/Lùi
    }
    
    // NẾU LÀ CHẾ ĐỘ TẬP: Hiển thị Bảng
    
    // Đảm bảo overflowY của rightCol được bật lại cho chế độ Bảng
    rightCol.style.overflowY = "scroll"; 
    
    const tableContainer = document.createElement("div"); // Thêm container để cuộn
    tableContainer.style.maxHeight = "calc(100vh - 100px)"; // Giảm chiều cao một chút
    tableContainer.style.overflowY = "auto";
    tableContainer.style.width = "100%";

    const table = document.createElement("table");
    table.style.width = "95%";
    table.style.borderCollapse = "collapse";
    table.style.margin = "0 auto";
    table.innerHTML = `
        <thead>
            <tr style="background: #e0e0e0;">
                <th>r</th><th>THOA</th><th>TG</th><th>R</th><th>VET</th>
            </tr>
        </thead>
        <tbody>
        </tbody>
    `;
    const tbody = table.querySelector('tbody');
    
    history.forEach(row => {
        const tr = document.createElement("tr");
        // Đảm bảo không gian hiển thị: word-break cho TG
        tr.innerHTML = `
            <td style="border: 1px solid #ddd; padding: 5px; text-align: center; width: 5%;"><b>${row.r}</b></td>
            <td style="border: 1px solid #ddd; padding: 5px; text-align: center; width: 25%;">${row.THOA}</td>
            <td style="border: 1px solid #ddd; padding: 5px; text-align: center; width: 35%; word-break: break-word;">${row.TG}</td>
            <td style="border: 1px solid #ddd; padding: 5px; text-align: center; width: 25%;">${row.R}</td>
            <td style="border: 1px solid #ddd; padding: 5px; text-align: center; width: 10%;">${row.VET}</td>
        `;
        tbody.appendChild(tr);
    });

    tableContainer.appendChild(table);
    rightCol.appendChild(tableContainer);
}