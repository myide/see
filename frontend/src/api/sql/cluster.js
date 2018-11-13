import axios from '../../libs/http';

const dbCluster = '/api/sqlmng/dbcluster/';

const dbConfs = '/api/sqlmng/dbconfs/';

export function GetDbList (params) {
    return axios({
        url: dbConfs,
        method: 'get',
        params
    });
}

export function GetClusterList (params) {
    return axios({
        url: dbCluster,
        method: 'get',
        params
    });
}

export function UpdateCluster (id, data) {
    return axios({
        url: dbCluster + id + '/',
        method: 'put',
        data: data
    });
}

export function CreateCluster (data) {
    return axios({
        url: dbCluster,
        method: 'post',
        data: data
    });
}

export function DeleteCluster (id) {
    return axios({
        url: dbCluster + id + '/',
        method: 'delete',
    });
}