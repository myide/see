import axios from '../../libs/http';

const dbConfs = '/api/sqlmng/dbconfs/';
const checkConnUrl = '/api/sqlmng/inception/conncheck/'
const GetDatabasesUrl = '/api/sqlmng/inception/showdatabases/'

export function GetDbList(params) {
    return axios({
        url: dbConfs,
        method: 'get',
        params
    });
}

export function UpdateDb(id, data) {
    return axios({
        url: dbConfs + id + '/',
        method: 'put',
        data: data
    });
}

export function CreateDb(data) {
    return axios({
        url: dbConfs,
        method: 'post',
        data: data
    });
}

export function DeleteDb(id) {
    return axios({
        url: dbConfs + id + '/',
        method: 'delete',
    });
}

export function CheckConn(data) {
    return axios({
        url: checkConnUrl,
        method: 'post',
        data: data
    });
}

export function GetDatabases(data) {
    return axios({
        url: GetDatabasesUrl,
        method: 'post',
        data: data
    });
}

