// ---------------- Tab Switcher ----------------
function switchTab(tab) {
  document.getElementById('tab-diagnosis').classList.remove('active');
  document.getElementById('tab-prediction').classList.remove('active');
  document.getElementById('tabBtnDiagnosis').classList.remove('active');
  document.getElementById('tabBtnPrediction').classList.remove('active');

  if (tab === 'diagnosis') {
    document.getElementById('tab-diagnosis').classList.add('active');
    document.getElementById('tabBtnDiagnosis').classList.add('active');
  } else {
    document.getElementById('tab-prediction').classList.add('active');
    document.getElementById('tabBtnPrediction').classList.add('active');
  }
}

//Diagnose Symptoms
function diagnoseSymptoms() {
  const symptoms = [
    { id: "sym1", name: "Da nhợt nhạt" },
    { id: "sym2", name: "Mệt mỏi" },
    { id: "sym3", name: "Hơi thở ngắn / khó thở" },
    { id: "sym4", name: "Tim đập nhanh" },
    { id: "sym5", name: "Gan hoặc lách to" },
    { id: "sym6", name: "Xương mặt biến dạng" }
  ];

  const selected = symptoms
    .filter(s => document.getElementById(s.id).checked)
    .map(s => s.name);

  let result = "<h3>Kết quả chẩn đoán:</h3>";

  if (selected.length === 0) {
    result += "<p>❌ Vui lòng chọn ít nhất một triệu chứng.</p>";
  }
  else if (selected.length <= 2) {
    result += "<p>🟢 Có thể là thể nhẹ hoặc người lành. Cần xét nghiệm máu để chắc chắn.</p>";
  }
  else if (selected.length <= 4) {
    result += "<p>🟠 Có nguy cơ Thalassemia thể nhẹ hoặc trung bình.</p>";
  }
  else {
    result += "<p>🔴 Khả năng cao Thalassemia thể nặng. Nên khám chuyên khoa ngay.</p>";
  }

  result += "<hr><b>Triệu chứng ghi nhận:</b> " + selected.join(", ");

  const div = document.getElementById("result-diagnosis");
  div.innerHTML = result;
  div.style.display = "block";
}

// ---------------- Genetic Prediction ----------------
function predict() {
  const fGene = document.getElementById("fatherGene").value;
  const mGene = document.getElementById("motherGene").value;

  let result = "<h3>Dự đoán di truyền cho con:</h3>";

  if (!fGene || !mGene) {
    alert("Vui lòng chọn kiểu gen cho cả cha và mẹ!");
    return;
  }

  // ============================
  // XỬ LÝ KIỂU GEN CHA (A_)
  // ============================
  let fatherFinal = fGene;
  if (fGene === "A_") {
    const gf = document.getElementById("grandfatherGene").value;
    const gm = document.getElementById("grandmotherGene").value;

    if (gf && gm) {
      // Nếu ông/bà có Aa hoặc aa → Cha chắc chắn là Aa (mang gen bệnh)
      if (gf === "Aa" || gm === "Aa" || gf === "aa" || gm === "aa") {
        fatherFinal = "Aa";
      }
      // Nếu cả ông lẫn bà đều AA → Cha chắc chắn AA
      else if (gf === "AA" && gm === "AA") {
        fatherFinal = "AA";
      }
    }
  }

  // ============================
  // XỬ LÝ KIỂU GEN MẸ (A_)
  // ============================
  let motherFinal = mGene;
  if (mGene === "A_") {
    const gf = document.getElementById("grandfatherGene_m").value;
    const gm = document.getElementById("grandmotherGene_m").value;

    if (gf && gm) {
      if (gf === "Aa" || gm === "Aa" || gf === "aa" || gm === "aa") {
        motherFinal = "Aa";
      }
      else if (gf === "AA" && gm === "AA") {
        motherFinal = "AA";
      }
    }
  }

  // ============================
  // LOGIC MẸNĐEN (SAU KHI ĐÃ XỬ LÝ A_)
  // ============================
  let outcomes = "";

  if (fatherFinal === "AA" && motherFinal === "AA")
    outcomes = "100% bình thường (AA)";

  else if ((fatherFinal === "Aa" && motherFinal === "AA") ||
           (fatherFinal === "AA" && motherFinal === "Aa"))
    outcomes = "50% bình thường (AA), 50% mang gen (Aa)";

  else if (fatherFinal === "Aa" && motherFinal === "Aa")
    outcomes = "25% bình thường (AA), 50% mang gen (Aa), 25% bị bệnh (aa)";

  else if ((fatherFinal === "aa" && motherFinal === "Aa") ||
           (fatherFinal === "Aa" && motherFinal === "aa"))
    outcomes = "50% mang gen (Aa), 50% bị bệnh (aa)";

  else if (fatherFinal === "aa" && motherFinal === "aa")
    outcomes = "100% con bị bệnh (aa)";

  else
    outcomes = "Không xác định được kết quả.";

  result += `<p>${outcomes}</p>`;

  result += `<p><b>Kiểu gen CHA sau khi xét ông bà:</b> ${fatherFinal}</p>`;
  result += `<p><b>Kiểu gen MẸ sau khi xét ông bà:</b> ${motherFinal}</p>`;

  result += "<p><b>Giải thích:</b> Kết quả dựa trên quy luật di truyền Mendel (Punnett Square).</p>";

  const div = document.getElementById("result");
  div.innerHTML = result;
  div.style.display = "block";
}

function toggleGrandParents(parent) {
  const gene = document.getElementById(
    parent === "father" ? "fatherGene" : "motherGene"
  ).value;

  const grandBox = document.getElementById(
    parent === "father" ? "father-grandparents" : "mother-grandparents"
  );

  const familyHistoryLabel = document.getElementById(
    parent === "father" ? "fatherFamilyHistory" : "motherFamilyHistory"
  ).parentElement;

  const symptomsLabel = document.getElementById(
    parent === "father" ? "fatherSymptoms" : "motherSymptoms"
  ).parentElement;

  if (gene === "A_") {
    grandBox.style.display = "block";
    familyHistoryLabel.style.setProperty("display", "flex", "important");
    symptomsLabel.style.setProperty("display", "flex", "important");
  } else {
    grandBox.style.display = "none";
    familyHistoryLabel.style.setProperty("display", "none", "important");
    symptomsLabel.style.setProperty("display", "none", "important");
  }
}

