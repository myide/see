
export function contains (arr, obj) {
    var i = arr.length;
    while (i--) {
        if (arr[i].id === obj) {
            return true;
        }
    }
    return false;
}
