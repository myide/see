<style lang="less">
    @import './login.less';
</style>

<template>
    <div class="login" @keydown.enter="handleSubmit">
        <div class="login-con">
            <Card :bordered="false">
                <p slot="title">
                    <Icon type="log-in"></Icon>
                    欢迎登录
                </p>
                <div class="form-con">
                    <Form ref="loginForm" :model="form" :rules="rules">
                        <FormItem prop="userName">
                            <Input v-model="form.userName" placeholder="请输入用户名">
                                <span slot="prepend">
                                    <Icon :size="16" type="person"></Icon>
                                </span>
                            </Input>
                        </FormItem>
                        <FormItem prop="password">
                            <Input type="password" v-model="form.password" placeholder="请输入密码">
                                <span slot="prepend">
                                    <Icon :size="14" type="locked"></Icon>
                                </span>
                            </Input>
                        </FormItem>
                        <FormItem>
                            <Button @click="handleSubmit" type="primary" long>登录</Button>
                        </FormItem>
                    </Form>
                    <p class="login-tip">输入任意用户名和密码即可</p>
                </div>
            </Card>
        </div>
    </div>
</template>

<script>
import Cookies from 'js-cookie';
import { Login } from '@/api/login'

export default {
    data () {
        return {
            form: {
                userName: '',
                password: ''
            },
            rules: {
                userName: [
                    { required: true, message: '账号不能为空', trigger: 'blur' }
                ],
                password: [
                    { required: true, message: '密码不能为空', trigger: 'blur' }
                ]
            }
        };
    },

    created() {
        let user = localStorage.getItem('user')
        this.form.userName = user ? user : 'admin'
    },

    methods: {
        handleSubmit () {
            this.$refs.loginForm.validate((valid) => {
                if (valid) {
                    this.login(this.form.userName, this.form.password) 
                    /* this.$store.commit('setAvator', 'https://ss1.bdstatic.com/70cFvXSh_Q1YnxGkpoWK1HF6hhy/it/u=3448484253,3685836170&fm=27&gp=0.jpg');
                    if (this.form.userName === 'iview_admin') {
                        Cookies.set('access', 0);
                    } else {
                        Cookies.set('access', 1);
                    }
                    this.$router.push({
                        name: 'home_index'
                    });
                    */
                }
            });
        },

        login (user, password) {
            const data = { username: user, password: password }
            Login(data)
            .then(response => {
                let token = response.data.token
                // cookie写入信息
                Cookies.set('token',token)                           
                Cookies.set('user', user);
                Cookies.set('password', password);
                localStorage.setItem('user', user)
                // 跳转到首页
                this.$router.push({
                    name: 'home_index'
                }); 
                // 显示提示信息
                this.$Message.success({
                    content: '登陆成功',
                    duration: 3
                });

            })
            .catch(error => {
                this.$Message.error({
                    content: '登录失败（' + error.request.response + '）',
                    duration: 5
                });

            })

        },


    }
};
</script>

<style>

</style>
