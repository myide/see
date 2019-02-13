import axios from 'axios';

const authUrl = '/api/api-token-auth/';
const unifiedAuthUrl = '/api/account/unitaryauth/';

export function Login (data) {
    return axios({
        url: authUrl,
        method: 'post',
        data: data
    });
};

export function UnifiedAuth (data) {
    return axios({
        url: unifiedAuthUrl,
        method: 'post',
        data: data
    });
};