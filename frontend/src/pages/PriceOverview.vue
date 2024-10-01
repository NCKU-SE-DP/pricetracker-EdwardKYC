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
    padding: 3% 5%;
    background: #f3f3f3;
    min-height: calc(100vh - 4.5em);
    box-sizing: border-box;
    overflow-x: hidden; /* 預設情況下不允許橫向滾動 */
}

/* 針對小螢幕調整 .wrapper 的內邊距，避免過大的邊距 */
@media (max-width: 768px) {
    .wrapper {
        padding: 2% 4%; /* 小螢幕上減少內邊距 */
        overflow-x: auto; /* 小螢幕時允許橫向滾動 */
    }
}

/* 調整 .prices 的排版，確保在小螢幕上正常顯示 */
.prices {
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
    gap: 1em; /* 使用 gap 來確保項目之間的間距 */
    overflow-x: hidden; /* 預設不允許橫向滾動 */
}

/* 根據螢幕大小調整 .category 的大小和排列方式 */
.category {
    margin: 1em;
    flex-grow: 1;
    flex-basis: calc(33.33% - 2em); /* 大螢幕時，三欄佈局，每欄佔三分之一 */
}

/* 針對小螢幕的調整，單欄佈局 */
@media (max-width: 768px) {
    .category {
        flex-basis: calc(100% - 2em); /* 每欄佔全寬 */
        margin: 0.5em 0; /* 減少間距 */
    }

    .subtitle {
        font-size: 0.8em; /* 子標題字體縮小 */
    }

    h1 {
        font-size: 1.5em; /* 標題字體縮小 */
    }

    h3 {
        font-size: 1em; /* 其他標題字體縮小 */
    }
}

.subtitle {
    font-weight: normal;
    margin-top: 0.5em;
    text-align: center;
}

/* 如果超過容器寬度，允許橫向滾動 */
@media (max-width: 768px) {
    .prices {
        overflow-x: auto; /* 當內容超出時允許滾動 */
        display: inline-block; /* 小螢幕時使每個項目水平排列 */
        white-space: pre-wrap; /* 避免項目換行，保持在一行 */
    }

    .category {
        display: inline-block;
        width: auto;
        min-width: 300px; /* 設置最小寬度，確保元素可讀 */
    }
}
</style>