import axios from '../../libs/http';
const dbConfs = '/api/sqlmng/dbconfs/';

export function GetTableList(id) {
    return axios.get(dbConfs + id + '/tables/');
}

export function GetTableInfo(id, tableName) {
    return axios.get(dbConfs + id + '/table_info/?table_name=' + tableName);
}

export function GetSqlAdvisor (id, data) {
    return axios({
        url: dbConfs + id + '/sql_advisor/',
        method: 'post',
        data: data
    });
}

export function GetSqlSOAR (id, data) {
    return axios({
        url: dbConfs + id + '/sql_soar/',
        method: 'post',
        data: data
    });
}

export function GetTableRelatedStatus (id) {
    return axios.get(dbConfs + id + '/relate_permission/');
}
