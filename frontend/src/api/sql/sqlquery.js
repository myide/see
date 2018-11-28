import axios from '../../libs/http';
const dbConfs = '/api/sqlmng/dbconfs/';

export function GetTableList(id) {
    return axios.get(dbConfs + id + '/tables/');
}

export function GetTableInfo(id, tableName) {
    return axios.get(dbConfs + id + '/table_info/?table_name=' + tableName);
}

export function GetSqlAdvisor(id, sql) {
    return axios.get(dbConfs + id + '/sql_advisor/?sql=' + sql);
}

export function GetSqlSOAR(id, params) {
    return axios({
        url: dbConfs + id + '/sql_soar/',
        method: 'get',
        params
    })
}