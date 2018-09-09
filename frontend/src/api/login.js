import axios from '../libs/http';

const authUrl = '/api/api-token-auth/';

export function Login(data) {
    return axios({
        url: authUrl,
        method: 'post',
        data: data
    });
};