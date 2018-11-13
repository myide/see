export function ContainsIdList (arr, id) {  
    var i = arr.length;  
    while (i--) {  
        if (arr[i] === id) {  
            return true;  
        }  
    }  
    return false;  
}  
