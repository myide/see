
export function addDate (date, days) {
    var d = new Date(date);
    d.setDate(d.getDate() + days);
    var m = d.getMonth() + 1;
    return d.getFullYear() + '-' + m + '-' + d.getDate();
}
export function convertNumber (num) {
    if (num > 0 && num < 10) {
        num = '0' + num;
    }
    return num;
}

export function formatDate (date) {
    if (typeof (date) === 'string') {
        return date;
    }
    let year = date.getFullYear();
    let month = date.getMonth() + 1;
    let day = date.getDate();
    month = convertNumber(month);
    day = convertNumber(day);
    return year + '-' + month + '-' + day;
}

export function formatTime (time) {
    return time.split('.')[0].replace('T',' ')
}