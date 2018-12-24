//import axios from '../libs/http';
import axios from 'axios'

const authUrl = '/api/api-token-auth/';
const UnifiedAuthUrl = '/api/account/unitaryauth/'

export function Login(data) {
    return axios({
        url: authUrl,
        method: 'post',
        data: data
    });
};

export function UnifiedAuth(data) {
    return axios({
        url: UnifiedAuthUrl,
        method: 'post',
        data: data
    });
};