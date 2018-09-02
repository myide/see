
export function getSqlContent (sqlContent) {
    const sqlContentList = sqlContent.split(';')
    sqlContent = []
    sqlContentList.map( (item) => {
      if (item.length > 2) {
        sqlContent.push({
          value:item + ';',
        })
      }
    })
    return sqlContent
  }

export function handleBadgeData (steps) {
    let count = 0  // status不为0即纳入计数
    let badgeStatus = ''  // 最后一个不为0的step 状态，即为徽标状态
    for (let i in steps) {
      let step = steps[i]
      let status = step.status
      if (status != 0) {  // 不为0的状态
        count += 1
        if (i < steps.length - 1){
          if (steps[i+1] == 0){  // 后一位是状态0
            badgeStatus = status
          }
        } else {  // 最后一个元素
           badgeStatus = status
        }
      }
    }
    return {count:count, badgeStatus:badgeStatus}
  }


