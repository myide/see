
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

