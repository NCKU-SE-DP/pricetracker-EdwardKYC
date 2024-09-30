<template>
    <div class="wrapper">
        <h1>各類商品物價概覽</h1>
        <h3 v-if="!isLoading" class="subtitle">資料更新時間：{{updateTime}}</h3>
        <div class="prices">
            <CategoryPrice class="category" v-for="category in categoryList" :key="category"
                :category="category" :isLoading="isLoading" :errorMessage="errorMessage" :priceData="getPriceData(category)"></CategoryPrice>
        </div>
    </div>
</template>

<script>
import CategoryPrice from '@/components/CategoryPrice.vue';
import Categories from '@/constants/categories';
import { usePricesStore } from '@/stores/prices';

export default {
    name: 'PriceOverview',
    data() {
        return {
            prices: {},
        };
    },
    components: {
        CategoryPrice
    },
    computed: {
        categoryList() {
            return Object.keys(Categories);
        },
        isLoading(){
            const store = usePricesStore();
            return store.isLoading;
        },
        errorMessage(){
            const store = usePricesStore();
            return store.errorMessage;
        },
        updateTime(){
            const store = usePricesStore();
            return store.updatedTime;
        }
    },
    methods:{
        getPriceData(category){
            const store = usePricesStore();
            return store.getPricesByCategory(category);
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
    box-sizing: border-box;
}

/* 針對小螢幕調整 wrapper 的內邊距，避免過大的邊距 */
@media (max-width: 768px) {
    .wrapper {
        padding: 1em 1.5em;
    }
}

/* 調整 .prices 的排版，確保在小螢幕上正常顯示 */
.prices {
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
    gap: 1em; /* 使用 gap 來確保項目之間的間距 */
}

/* 根據螢幕大小調整 .category 的大小和排列方式 */
.category {
    margin: 1em;
    flex-grow: 1;
    flex-basis: calc(33.33% - 2em); /* 大螢幕時，三欄佈局，每欄佔三分之一 */
}

/* 針對中等螢幕的調整，兩欄佈局 */
@media (max-width: 992px) {
    .category {
        flex-basis: calc(50% - 2em); /* 每欄佔二分之一 */
    }
}

/* 針對小螢幕的調整，單欄佈局 */
@media (max-width: 768px) {
    .category {
        flex-basis: calc(100% - 2em); /* 每欄佔全寬 */
        margin: 0.5em 0; /* 減少間距 */
    }
}

.subtitle {
    font-weight: normal;
    margin-top: 0.5em;
    text-align: center;
}

</style>