<template>
    <nav class="navbar">
        <div class="title"> 
            <RouterLink to="/overview">價格追蹤小幫手</RouterLink>
            <span class="menu-btn" @click="toggleMenu">
                {{ isMenuVisible ? '✕' : '☰' }} <!-- 根據 isMenuVisible 切換符號 -->
            </span>
        </div>
        <ul class="options" v-if="isMenuVisible"> <!-- 使用 v-if 控制顯示 -->
            <li><RouterLink to="/overview">物價概覽</RouterLink></li>
            <li><RouterLink to="/trending">物價趨勢</RouterLink></li>
            <li><RouterLink to="/news">相關新聞</RouterLink></li>
            <li v-if="!isLoggedIn"><RouterLink to="/login">登入</RouterLink></li>
            <li v-else @click="logout">Hi, {{getUserName}}! 登出</li>
        </ul>
    </nav>
</template>

<script>
import { useAuthStore } from '@/stores/auth';

export default {
    name: 'NavBar',
    data() {
        return {
            isMenuVisible: false // 預設隱藏菜單
        };
    },
    computed: {
        isLoggedIn(){
            const userStore = useAuthStore();
            return userStore.isLoggedIn;
        },
        getUserName(){
            const userStore = useAuthStore();
            return userStore.getUserName;
        }
    },
    methods: {
        logout(){
            const userStore = useAuthStore();
            userStore.logout();
        },
        toggleMenu() {
            this.isMenuVisible = !this.isMenuVisible; // 切換菜單顯示狀態
        },
        handleResize() {
            if (window.innerWidth > 768) {
                this.isMenuVisible = true; // 大於768px時自動顯示
            } else if (!this.isMenuVisible) {
                this.isMenuVisible = false; // 小於768px時維持使用者的選擇
            }
        }
    },
    mounted() {
        window.addEventListener('resize', this.handleResize); // 監聽窗口大小變化
        this.handleResize(); // 初始化菜單顯示狀態
    },
    beforeUnmount() {
        window.removeEventListener('resize', this.handleResize); // 清除事件監聽
    }
};
</script>

<style scoped>
.navbar {
    display: flex;
    justify-content: space-between;
    background-color: #f3f3f3;
    padding: 1.5em;
    height: auto; /* 自動調整高度 */
    width: 100%;
    align-items: center;
    box-shadow: 0 0 5px #000000;
}

.navbar ul {
    list-style: none;
    display: flex;
    justify-content: space-around;
    margin: 0; /* 移除 margin */
    padding: 0; /* 移除 padding */
}

.title > a {
    font-size: 1.4em;
    font-weight: bold;
    color: #2c3e50 !important;
}

.navbar li {
    color: #575B5D;
    margin: 0 .5em;
    font-size: 1.2em;
}

.navbar li:hover {
    cursor: pointer;
    font-weight: bold;
}

.navbar a {
    text-decoration: none;
    color: #575B5D;
}

@media (max-width: 768px) {
    .navbar {
        padding: 0;
        flex-direction: column; /* 將導航欄垂直排列 */
        height: auto; /* 自動調整高度 */
        align-items: flex-start; /* 左對齊 */
    }
    .navbar ul {
        flex-direction: column; /* 將選項垂直排列 */
        width: 100%; /* 讓列表寬度填滿 */
        padding: 0; /* 移除 padding */
        border-top: 1px solid black; /* 在 ul 的頂部加上黑線 */
    }

    .navbar li {
        margin: 0.5em 0; /* 增加選項之間的間距 */
        width: 100%; /* 讓選項寬度填滿 */
        text-align: center; /* 左對齊選項文字 */
        border-bottom: 1px solid black; /* 在每個選項之間加上黑線 */
        padding: 0.5em 0; /* 增加一點內部填充讓線條不緊貼文字 */
        margin: 0;
    }

    .title {
        width: 100%;
        text-align: left; /* 左對齊標題 */
        position: relative; /* 讓打叉符號在標題內部浮動 */
        padding-left: 10px; /* 左側增加間距 */
        padding-right: 10px; /* 右側增加間距 */
    }

    .title > a {
        font-size: 1.2em; /* 放大標題字體大小 */
        padding: 0.5em 0;
    }

    .menu-btn {
        position: absolute;
        right: 10px; /* 讓符號靠右 */
        top: 50%;
        transform: translateY(-50%);
        font-size: 1.5em;
        cursor: pointer;
        color: #575B5D;
    }
}

/* 大於 768px 時隱藏符號 */
.menu-btn {
    display: none; /* 預設隱藏符號 */
}

@media (max-width: 768px) {
    .menu-btn {
        display: inline; /* 小於 768px 時顯示符號 */
    }
}
</style>
