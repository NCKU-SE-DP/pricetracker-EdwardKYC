<template>
    <div class="chart-container">
        <canvas id="trendingChart"></canvas>
    </div>
</template>

<script>
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default {
    props: ['data'],
    data() {
        return {
            chart: null
        }
    },
    mounted() {
        this.createChart(this.data);
    },
    watch: {
        data(newData, oldData) {
            if (newData !== oldData) {
                this.createChart(newData);
            }
        }
    },
    methods: {
        createChart(data) {
            if (this.chart) {
                this.chart.destroy();
            }
            const ctx = document.getElementById('trendingChart').getContext('2d');
            let prices = data.統計值.split(',').map(price => parseInt(price, 10));
            let labels = this.generateLabels(data.時間起點, data.時間終點, prices.length);

            // 處理前導0並調整起始標籤
            let firstNonZeroIndex = prices.findIndex(price => price !== 0);
            if (firstNonZeroIndex > 0) {
                prices = prices.slice(firstNonZeroIndex);
                labels = labels.slice(firstNonZeroIndex);
            }

            // 替換中間的0並記錄點的位置來標註
            let lastValidPrice = prices[0];
            const annotations = [];
            prices = prices.map((price, index) => {
                if (price === 0) {
                    annotations.push({ index, price: lastValidPrice });
                    return lastValidPrice;
                }
                lastValidPrice = price;
                return price;
            });

            this.chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: data.產品名稱,
                        data: prices,
                        fill: false,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1,
                        pointRadius: prices.map((_, index) => annotations.some(a => a.index === index) ? 5 : 3),
                        pointStyle: prices.map((_, index) => annotations.some(a => a.index === index) ? 'crossRot' : 'circle'),
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: false
                        }
                    },
                    animation: {
                        duration: 300,
                    },
                    responsive: true,
                    maintainAspectRatio: false,
                }
            });
        },

        generateLabels(startDate, endDate, count) {
            const start = new Date(startDate);
            const labels = [];
            for (let i = 0; i < count; i++) {
                const monthDate = new Date(start.getFullYear(), start.getMonth() + i, 1);
                labels.push(`${monthDate.getFullYear()}.${monthDate.getMonth() + 1}`.padStart(2, '0'));
            }
            return labels;
        }
    }
};
</script>
<style scoped>

.chart-container {
    position: relative;
    margin: auto;
    height: 30vh;
    width: 100%; /* 設置容器寬度為 100% */
    overflow-x: hidden; /* 預設大於768px不顯示橫向滾動 */
    overflow-y: hidden; /* 垂直方向不顯示滾動條 */
    white-space: nowrap; /* 確保容器內的元素不會自動換行 */
}

canvas {
    width: 100%; /* 大於 768px 時，圖表隨容器寬度縮放 */
    max-width: 100%; /* 確保 canvas 不會超過容器寬度 */
    height: auto; /* 保持高度與寬度比例一致 */
}

/* 小螢幕的調整 */
@media (max-width: 768px) {
    .chart-container {
        height: 50vh; /* 小螢幕上增加高度，確保圖表顯示區域足夠 */
        overflow-x: scroll; /* 小螢幕上允許橫向滾動 */
    }

    canvas {
        width: 1200px; /* 設定圖表在小螢幕上的固定寬度 */
        min-width: 1200px; /* 確保 canvas 不會縮小到小於 1200px */
        height: auto; /* 確保寬度變化時高度自動調整，保持比例 */
    }
}

</style>
