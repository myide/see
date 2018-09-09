import axios from '../../libs/http';

const chart = '/api/dashboard/chart/';

export function GetChartData(params) {
    return axios({
        url: chart,
        method: 'get',
        params
    });
};