import axios from '../../libs/http';

const authRules = '/api/sqlmng/authrules/';

export function GetAuthRules(params) {
    return axios({
        url: authRules,
        method: 'get',
        params
    });
}