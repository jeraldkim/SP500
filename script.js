$(document).ready(function() {
    // Fetch JSON from GitHub
    const jsonUrl = 'https://raw.githubusercontent.com/jeraldkim/SP500/main/sp500_companies.json';

    fetch(jsonUrl)
        .then(response => response.json())
        .then(data => {
            // Update last-updated date
            const lastDate = data[0]?.Date || 'Unknown';
            $('#last-updated').text(`Last Updated: ${lastDate}`);

            // Initialize DataTable
            $('#sp500Table').DataTable({
                data: data,
                columns: [
                    { data: 'Symbol' },
                    { data: 'Security' },
                    { data: 'GICS Sector' },
                    { data: 'ClosePrice', render: (data) => data ? data.toFixed(2) : 'N/A' },
                    {
                        data: 'DailyChangePercent',
                        render: (data) => {
                            if (!data) return 'N/A';
                            const className = data >= 0 ? 'positive' : 'negative';
                            return `<span class="${className}">${data.toFixed(2)}%</span>`;
                        }
                    }
                ],
                pageLength: 25,
                order: [[4, 'desc']], // Sort by Daily Change by default
                responsive: true
            });
        })
        .catch(error => {
            console.error('Error fetching JSON:', error);
            $('#last-updated').text('Error loading data');
        });
});
