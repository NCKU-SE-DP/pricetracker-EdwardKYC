<template>
    <div class="wrapper">
        <h1>物價趨勢</h1>
        <div class="content">
            <div class="selects">

                <select v-model="selectedCategory">
                    <option disabled value="">請選擇商品類別</option>
                    <option v-for="category in categoryKeys" :key="category" :value="category">{{
                        categoryName(category)}}</option>
                </select>
                <select v-model="selectedProduct">
                    <option disabled value="">請選擇商品</option>
                    <option v-for="product in products" :key="product.產品名稱" :value="product">{{ product.產品名稱 }}</option>
                </select>
            </div>
            <div v-if="selectedProduct" class="visualize">
                <TrendingChart v-if="selectedProduct" :data="selectedProduct"></TrendingChart>
                <TrendingTable v-if="selectedProduct" :data="selectedProduct"></TrendingTable>
            </div>
        </div>
    </div>
</template>

<script>
import { usePricesStore } from '@/stores/prices';
import Categories from '@/constants/categories';
import TrendingTable from '@/components/TrendingTable.vue';
import TrendingChart from '@/components/TrendingChart.vue';

export default {
    components: {
        TrendingTable,
        TrendingChart
    },
    data() {
        return {
            selectedCategory: '',
            selectedProduct: '',
            productList: [],
        };
    },
    computed: {
        store() {
            return usePricesStore();
        },
        categoryKeys() {
            return Object.keys(Categories);
        },
        products() {
            return this.selectedCategory ? this.store.getPricesByCategory(this.selectedCategory) : [];
        },
    },
    methods: {
        categoryName(category) {
            return Categories[category];
        }
    },
    watch: {
        selectedCategory() {
            this.selectedProduct = '';
            const store = usePricesStore();
            this.productList = store.getProductList(this.selectedCategory);
            this.productData = null;
        },
        selectedProduct() {
            console.log(this.selectedProduct);
        }
    },
    created() {
        const store = usePricesStore();
        store.fetchPrices();
    }
};
</script>


<style scoped>
.wrapper {
    padding: 3em 5em;
    background: #f3f3f3;
    min-height: calc(100vh - 4.5em);
    height: calc(100% - 4.5em);
    box-sizing: border-box;
    width: 100%;
}

/* 調整內容容器，使其在小螢幕上自適應 */
.content {
    margin-top: 2em;
    background-color: #fff;
    border-radius: 1em;
    padding: 2em;
    width: 100%;
    max-width: 100%;
}

/* 選擇器在小螢幕上垂直排列 */
.selects {
    display: flex;
    justify-content: flex-start;
    flex-wrap: wrap;
}

.selects>select {
    padding: .5em;
    font-size: 1.1em;
    margin-right: 1em;
    margin-bottom: 1em; /* 增加垂直間距 */
    border-radius: .5em;
    border: 1px solid #ccc;
    outline: none;
    cursor: pointer;
    appearance: auto !important;
}

/* 調整圖表和表格容器的顯示方式，使其在小螢幕上堆疊 */
.visualize > * {
    flex: 1 1 50%;
    box-sizing: border-box;
    padding: 1em;
}

/* 小螢幕響應式設計 */
@media (max-width: 768px) {
    .wrapper {
        padding: 1.5em 2em; /* 調整 padding 以適應小螢幕 */
    }

    .selects {
        flex-direction: column; /* 垂直排列選擇器 */
        align-items: flex-start; /* 靠左對齊 */
    }

    .selects > select {
        width: 100%; /* 讓選擇器在小螢幕上填滿寬度 */
        margin-right: 0;
    }

    .visualize > * {
        flex: 1 1 100%; /* 在小螢幕上每個元素都佔據 100% 寬度 */
        padding: 0.5em 0; /* 調整 padding 讓內容更緊湊 */
    }
}

</style>