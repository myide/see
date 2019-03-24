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
                        <FormItem label="登录类型">
                            <RadioGroup v-model="loginType">
                                <Radio label="common">普通登录</Radio>
                                <Radio label="unified">统一认证</Radio>
                            </RadioGroup>
                        </FormItem>
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
                    <p class="login-tip"></p>
                </div>
            </Card>
        </div>
    </div>
</template>

<script>
import Cookies from 'js-cookie';
import { Login, UnifiedAuth } from '@/api/login'

export default {
    data () {
        return {
            loginType: '',
            authCode:'',
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
        let logintype = localStorage.getItem('logintype')
        this.loginType = logintype ? logintype : 'common'
    },

    methods: {
        handleSubmit () {
            this.$refs.loginForm.validate((valid) => {
                if (valid) {
                    if (this.loginType == 'unified') {
                        this.Unified(this.form.userName, this.form.password) 
                    } else {
                        this.login(this.form.userName, this.form.password) 
                    }
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
                localStorage.setItem('logintype', this.loginType)
                // 跳转到首页
                this.$router.push({
                    name: 'otherRouter'
                }); 
                // 显示提示信息
                this.$Message.success({
                    content: '登陆成功',
                    duration: 3
                });

            })
            .catch(error => {
                this.$Message.error({
                    content: '登录失败（用户名或密码错误）',
                    duration: 5
                });

            })

        },

        Unified (user, password) {
            const data = { username: user, password: password }
            UnifiedAuth(data)
            .then(response => {
                this.login(user, password) 
            })
        }

    }
};
</script>

<style>

</style>
