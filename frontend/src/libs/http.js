/**
 * Created by superman on 17/2/16.
 * http配置
 */

import Cookies from 'js-cookie';
import axios from 'axios';
import store from '../store';
import { router } from '../router';
import Vue from 'vue';
import iView from 'iview';

// axios 配置
axios.defaults.timeout = 30000;

function permerror(nodesc, title, desc) {
    iView.Notice.error({
        duration: 10,
        title: title,
        desc: nodesc ? '' : desc
    });
}

// http request 拦截器
axios.interceptors.request.use(
    function(config) {
        let token = Cookies.get('token')
        if (token) { // 获取到了本地的token
            config.headers.Authorization = 'JWT ' + token
        }
        return config
    },
    err => {
        return Promise.reject(err)
    })

// http response 拦截器
axios.interceptors.response.use(
    (response) => {
        return response
    },
    error => {
        console.log(iView)

        if (error.response) {
            //console.log('response_error:', error.response)
            switch (error.response.status) {
                case 400:
                    permerror(false, error.response.request.statusText, error.response.request.responseText)
                    break

                case 401: // 拦截验证token失败的请求，清除token信息并跳转到登录页面
                    store.commit('logout')
                    router.push({
                        name: 'login'
                    })
                    break

                case 403:
                    permerror(false, error.response.statusText, error.response.data.detail)
                    break

                case 500:
                    permerror(false, error.response.status, error.response.statusText)
                    break

            }
        }
        // console.log(JSON.stringify(error));//console : Error: Request failed with status code 402
        return Promise.reject(error) // 返回错误信息

    })

export default axios