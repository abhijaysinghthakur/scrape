document.addEventListener('DOMContentLoaded', () => {
    const progressLog = document.getElementById('progress-log');
    const reportContent = document.getElementById('report-content');
    const pathParts = window.location.pathname.split('/');
    const competitorId = pathParts[pathParts.length - 1];

    const eventSource = new EventSource(`/api/stream-scan/${competitorId}`);

    eventSource.onmessage = function(event) {
        const data = event.data;
        const logEntry = document.createElement('p');
        
        if (data.startsWith('STATUS:')) {
            logEntry.textContent = `> ${data.substring(8)}`;
            progressLog.appendChild(logEntry);
        } else if (data.startsWith('REPORT:')) {
            const reportText = data.substring(7).replace(/\|\|\|/g, '\n');
            const formattedHtml = reportText.replace(/\n/g, '<br>').replace(/### (.*?)(<br>|$)/g, '<h3>$1</h3>').replace(/- (.*?)(<br>|$)/g, '<li>$1</li>');
            
            progressLog.style.display = 'none';
            reportContent.innerHTML = formattedHtml;
            reportContent.style.display = 'block';
        } else if (data === 'DONE') {
            eventSource.close();
            // Optional: Add a final message if no report was generated
            if (reportContent.innerHTML === '') {
                 progressLog.innerHTML += '<p>> Process complete.</p>';
            }
        }
    };

    eventSource.onerror = function() {
        const errorEntry = document.createElement('p');
        errorEntry.style.color = 'red';
        errorEntry.textContent = '> Connection to server lost. Please try again.';
        progressLog.appendChild(errorEntry);
        eventSource.close();
    };
});