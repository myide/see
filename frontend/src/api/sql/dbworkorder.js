import axios from '../../libs/http';

const dbWorkOrder = '/api/sqlmng/dbworkorder/';

export function GetDbWorkOrderList (params) {
    return axios({
        url: dbWorkOrder,
        method: 'get',
        params
    });
}

export function UpdateDbWorkOrder (id, data) {
    return axios({
        url: dbWorkOrder + id + '/',
        method: 'put',
        data: data
    });
}

export function CreateDbWorkOrder (data) {
    return axios({
        url: dbWorkOrder,
        method: 'post',
        data: data
    });
}

export function ManageDbWorkOrder (data) {
    let urnMap = {
        1: 'database_order_approve',
        2: 'database_order_disapprove',
        3: 'database_order_reject'
    }
    let status = data.status;
    let urn = urnMap[status];
    return axios({
        url: dbWorkOrder + data.id + '/' + urn + '/',
        method: 'post',
        data: data
    });
}
