// Handle barcode upload form submission
document.getElementById("uploadForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    
    let fileInput = document.getElementById("fileInput").files[0];
    if (!fileInput) return;

    let formData = new FormData();
    formData.append("file", fileInput);

    document.getElementById("status").innerHTML = '<p class="status info">Uploading...</p>';
    document.getElementById("barcodeResults").style.display = "none";
    
    try {
        let response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        let result = await response.json();
        
        if (response.ok) {
            document.getElementById("status").innerHTML = '<p class="status success">Barcode scanned successfully!</p>';
            displayBarcodeResults(result);
        } else {
            document.getElementById("status").innerHTML = `<p class="status error">Error: ${result.error || 'Unknown error'}</p>`;
        }
    } catch (error) {
        document.getElementById("status").innerHTML = `<p class="status error">Error: ${error.message}</p>`;
    }
});

// Handle paste event for images
document.addEventListener("paste", async (event) => {
    let items = (event.clipboardData || event.originalEvent.clipboardData).items;
    for (let item of items) {
        if (item.kind === "file" && item.type.startsWith("image/")) {
            let file = item.getAsFile();
            let formData = new FormData();
            formData.append("file", file);

            document.getElementById("status").innerHTML = '<p class="status info">Uploading...</p>';
            document.getElementById("barcodeResults").style.display = "none";

            try {
                let response = await fetch("/upload", {
                    method: "POST",
                    body: formData
                });

                let result = await response.json();
                
                if (response.ok) {
                    document.getElementById("status").innerHTML = '<p class="status success">Barcode scanned successfully!</p>';
                    displayBarcodeResults(result);
                } else {
                    document.getElementById("status").innerHTML = `<p class="status error">Error: ${result.error || 'Unknown error'}</p>`;
                }
            } catch (error) {
                document.getElementById("status").innerHTML = `<p class="status error">Error: ${error.message}</p>`;
            }
        }
    }
});

// Handle parse receipt button click
document.getElementById("parseButton").addEventListener("click", async () => {
    let text = document.getElementById("pasteArea").value;
    if (!text.trim()) {
        document.getElementById("pasteStatus").innerHTML = '<p class="status error">Please enter text to parse</p>';
        return;
    }

    document.getElementById("pasteStatus").innerHTML = '<p class="status info">Parsing...</p>';
    document.getElementById("receiptResults").style.display = "none";

    try {
        let response = await fetch("/parse_receipt", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ text: text })
        });

        let result = await response.json();
        
        if (response.ok) {
            document.getElementById("pasteStatus").innerHTML = '<p class="status success">Receipt parsed successfully!</p>';
            displayReceiptResults(result.items);
        } else {
            document.getElementById("pasteStatus").innerHTML = `<p class="status error">Error: ${result.error || 'Unknown error'}</p>`;
        }
    } catch (error) {
        document.getElementById("pasteStatus").innerHTML = `<p class="status error">Error: ${error.message}</p>`;
    }
});

// Handle send to Google Sheets button click
document.getElementById("sendSheetButton").addEventListener("click", async () => {
    let response = await fetch("/save_to_sheets", {
        method: "POST",
    });

    let result = await response.text();
    document.getElementById("sendSheetStatus").innerText = result;
});

// Helper function to display barcode scan results
function displayBarcodeResults(data) {
    let container = document.getElementById("barcodeResults");
    
    if (Array.isArray(data) && data.length > 0) {
        // Check if it's an array of objects (structured data)
        if (typeof data[0] === 'object') {
            let html = '<h3>Scanned Products</h3><table><thead><tr>';
            
            // Create headers from object keys
            Object.keys(data[0]).forEach(key => {
                html += `<th>${key.replace(/_/g, ' ').toUpperCase()}</th>`;
            });
            html += '</tr></thead><tbody>';
            
            // Create rows
            data.forEach(item => {
                html += '<tr>';
                Object.values(item).forEach(value => {
                    html += `<td>${value !== null && value !== undefined ? value : 'N/A'}</td>`;
                });
                html += '</tr>';
            });
            html += '</tbody></table>';
            container.innerHTML = html;
        } else {
            // Simple array display
            container.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
        }
        container.style.display = "block";
    }
}

// Helper function to display receipt parsing results
function displayReceiptResults(items) {
    let container = document.getElementById("receiptResults");
    
    if (items && items.length > 0) {
        let html = '<h3>Parsed Receipt Items</h3><table><thead><tr>';
        html += '<th>ITEM NAME</th><th>PRICE</th><th>ORIGINAL NAME</th>';
        html += '</tr></thead><tbody>';
        
        items.forEach(item => {
            html += '<tr>';
            html += `<td>${item.simple_name || 'N/A'}</td>`;
            html += `<td>€${item.price !== null && item.price !== undefined ? item.price.toFixed(2) : 'N/A'}</td>`;
            html += `<td>${item.original_name || 'N/A'}</td>`;
            html += '</tr>';
        });
        html += '</tbody></table>';
        container.innerHTML = html;
        container.style.display = "block";
    }
}
