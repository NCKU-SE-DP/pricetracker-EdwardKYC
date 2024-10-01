<template>
    <div class="category-price-wrapper">
        <h2>{{ categoryName }}</h2>
        <div v-if="isLoading">Loading...</div>
        <div v-if="errorMessage" class="error">{{ errorMessage }}</div>
        <table v-if="!isLoading && !errorMessage">
            <thead>
                <tr>
                    <th>商品名稱</th>
                    <th>規格</th>
                    <th>{{latestDataTime}} 最新價格</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="data in priceData" :key="data.編號">
                    <td>{{ data.產品名稱 }}</td>
                    <td>{{ data.規格 }}</td>
                    <td>{{ latestPrice(data.統計值) }}</td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script>
import Categories from '@/constants/categories';

export default {
    props: {
        category: {
            type: String,
            required: true
        },
        priceData: {
            type: Array,
            required: true
        },
        isLoading: {
            type: Boolean,
            required: true
        },
        errorMessage: {
            type: String,
            required: false
        },
    },
    computed: {
        categoryName() {
            return Categories[this.category];
        },
        latestDataTime(){
            let timeTmp = this.priceData[0].時間終點.split('-');
            return timeTmp[0] + '.' + timeTmp[1];
        }
    },
    methods: {
        latestPrice(prices_str) {
            let number = prices_str.split(',').map(Number);
            let i = number.length - 1;
            while (i >= 0 && number[i]==0) {
                i--;
            }
            return i==-1 ? "-" : number[i];
        }
    }
};
</script>
<style scoped>
.error {
    color: red;
}
table {
    width: 100%;
    border-collapse: collapse;
    background-color: white;
    /* text-align: center; */
}
th, td {
    border: 1px solid #ddd;
    text-align: center;
    padding: .5em 1em;
}
th{
    background-color: #355f81;
    color: white;
}
h2{
    margin-bottom: .5em;
    font-size: 1.5em;
    font-weight: bold;
}
.category-price-wrapper{
    background-color: white;
    border-radius: 1em;
    padding: 2em; /* 大螢幕的內邊距 */
}

/* 針對小螢幕調整 padding，按比例縮小 */
@media (max-width: 768px) {
    .category-price-wrapper {
        padding: calc(2em * 0.5); /* 按 50% 的比例縮小內邊距 */
    }
    h2 {
        font-size: calc(1.5em * 0.9); /* 字體按比例縮小 */
    }
}
</style>
