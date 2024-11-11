let cell_1_ues = [];
let cell_2_ues = [];
let cell_3_ues = [];
let cell_loads = {
    cell_1: 0,
    cell_2: 0,
    cell_3: 0
};

const UE_GENERATION_INTERVAL = 1000; // 1 saniye aralıklarla UE üret
const UE_LIFESPAN = 10000; // Her UE'nin yaşam süresi 5 saniye

// Rasgele UE üretme fonksiyonu
function generateUE() {
    const ueCount = Math.floor(Math.random() * 5) + 1; // 1 ile 5 arasında UE sayısı
    const ueData = [];
    for (let i = 0; i < ueCount; i++) {
        const ueId = `UE_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
        const cellId = `cell_${Math.floor(Math.random() * 3) + 1}`; // cell_1, cell_2, cell_3 rastgele seçim
        ueData.push({ id: ueId, cell: cellId });
        
        // UE'yi ilgili hücreye ekleyelim
        if (cellId === "cell_1") cell_1_ues.push(ueId);
        else if (cellId === "cell_2") cell_2_ues.push(ueId);
        else if (cellId === "cell_3") cell_3_ues.push(ueId);
    }

    updateCellCounts();
    setTimeout(removeUE, UE_LIFESPAN, ueData); // UE'yi 5 saniye sonra kaldır
}

// UE'leri silme fonksiyonu
function removeUE(ueData) {
    ueData.forEach(ue => {
        if (ue.cell === "cell_1") {
            const index = cell_1_ues.indexOf(ue.id);
            if (index > -1) cell_1_ues.splice(index, 1);
        } else if (ue.cell === "cell_2") {
            const index = cell_2_ues.indexOf(ue.id);
            if (index > -1) cell_2_ues.splice(index, 1);
        } else if (ue.cell === "cell_3") {
            const index = cell_3_ues.indexOf(ue.id);
            if (index > -1) cell_3_ues.splice(index, 1);
        }
    });
    updateCellCounts();
}

// Hücre yüklerini güncelleme fonksiyonu
function updateCellCounts() {
    cell_loads.cell_1 = cell_1_ues.length;
    cell_loads.cell_2 = cell_2_ues.length;
    cell_loads.cell_3 = cell_3_ues.length;

    // Sol üst köşedeki UE sayıları güncelleniyor
    document.getElementById("count-cell-1").innerText = cell_loads.cell_1;
    document.getElementById("count-cell-2").innerText = cell_loads.cell_2;
    document.getElementById("count-cell-3").innerText = cell_loads.cell_3;

    // Hücrelerin load değerlerini JSON formatında konsola yazalım
    const cellLoadData = JSON.stringify({
        "cell_1": cell_loads.cell_1,
        "cell_2": cell_loads.cell_2,
        "cell_3": cell_loads.cell_3
    });
    updateConsole(cellLoadData);

    // Yük aşımı durumunu kontrol et ve POST isteği gönder
    checkTrafficSteering();
}

// Konsole log yazma
function updateConsole(message) {
    const consoleOutput = document.getElementById("console");
    consoleOutput.innerHTML = message;
}

// Yük aşımını kontrol etme ve yönlendirme yapma
function checkTrafficSteering() {
    Object.keys(cell_loads).forEach(cellId => {
        if (cell_loads[cellId] > 10) {
            const targetCell = Object.keys(cell_loads).reduce((minCell, cell) => {
                return cell_loads[cell] < cell_loads[minCell] ? cell : minCell;
            }, cellId);

            if (targetCell !== cellId) {
                const ueToMove = {
                    current_cell: cellId,
                    target_cell: targetCell,
                    ue_id: `UE_${Date.now()}` // Test için rastgele bir UE ID
                };

                // xApp'e POST isteği gönder
                fetch("http://localhost:5001/traffic_steering", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(ueToMove)
                }).then(response => response.json())
                  .then(data => {
                      updateConsole(`Steering triggered: Moving ${ueToMove.ue_id} from ${cellId} to ${targetCell}`);
                  });
            }
        }
    });
}

// UE üretimini başlat
setInterval(generateUE, UE_GENERATION_INTERVAL);  // 3 saniye aralıklarla UE üret
