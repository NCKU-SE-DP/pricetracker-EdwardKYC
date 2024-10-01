<template>
    <div class="login-page">
        <h1>使用者登入</h1>
        <div class="container">
            <form @submit.prevent="login">
                <input v-model="username" type="text" placeholder="Username" required>
                <input v-model="password" type="password" placeholder="Password" required>
                <p v-if="loginError" class="error">{{ loginError }}</p>
                <div class="ops">
                    <button type="button" id="register"><RouterLink to="/register">註冊</RouterLink></button>
                    <button type="submit" id="login">登入</button>
                </div>
            </form>
        </div>
    </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth';

export default {
    data() {
        return {
            username: '',
            password: ''
        };
    },
    methods: {
        login() {
            const userStore = useAuthStore();
            userStore.login(this.username, this.password);
        }
    },
    computed: {
        loginError(){
            const userStore = useAuthStore();
            return userStore.getLoginError;
        }
    }
}
</script>

<style scoped>
.login-page {
    padding: 1% 2%; /* 使用百分比來設置內邊距 */
    background: #f3f3f3;
    min-height: calc(100vh - 4.5em);
    height: calc(100% - 4.5em);
    box-sizing: border-box;
}

.error {
    color: red;
}

.container {
    margin-top: 2em;
    background: #fff;
    padding: 4%; /* 使用百分比來設置內部填充 */
    border-radius: 1em;
    box-shadow: 0 0 10px rgba(0, 0, 0, .1);
    max-width: 100%; /* 容器寬度設置為最大 100% */
    box-sizing: border-box;
}

form {
    display: flex;
    flex-direction: column;
}

form > input {
    margin: 1em 0; /* 使用比例的間距 */
    padding: 1em 2em; /* 調整內部填充為比例 */
    font-size: 1.2em;
    border: 1px solid #ccc;
    border-radius: 0.5em;
}

.ops {
    margin-top: 1em;
    display: flex;
    justify-content: center;
    flex-wrap: wrap; /* 允許按鈕換行，以便在小螢幕下排列 */
    gap: 1em; /* 使用 gap 來設置按鈕間距 */
}

.ops > button {
    padding: 1em 2em; /* 使用百分比來設置按鈕大小 */
    font-size: 1.2em;
    border: none;
    border-radius: 0.5em;
    cursor: pointer;
    max-width: 100%; /* 防止按鈕超出容器寬度 */
    width: auto; /* 自適應寬度 */
}

#register {
    background-color: #F3F3F3;
    border: 1px solid #ccc;
}

#register > a {
    text-decoration: none;
    color: #000;
}

#register:hover {
    background-color: #e8e8e8;
}

#login {
    background-color: #5bc0de;
    color: #fff;
}

#login:hover {
    background-color: #46b8da;
}

/* 小螢幕的調整 */
@media (max-width: 768px) {
    .login-page {
        padding: 3% 5%; /* 小螢幕上減少邊距 */
    }

    .container {
        padding: 4%; /* 在小螢幕上減少內部填充 */
        max-width: 100%; /* 小螢幕時佔據全寬 */
    }

    form > input {
        font-size: 1em; /* 在小螢幕上減小字體大小 */
        padding: 0.8em 1.5em; /* 調整填充大小 */
    }

    .ops {
        flex-direction: column; /* 將按鈕改為縱向排列以適應小螢幕 */
    }

    .ops > button {
        font-size: 1em; /* 調整按鈕字體大小 */
        padding: 0.8em 1.5em; /* 調整按鈕大小 */
        width: 100%; /* 按鈕在小螢幕上佔據全寬 */
        max-width: 100%; /* 防止超出容器 */
    }
}

</style>