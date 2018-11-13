export function CascaderData (dbs) {
	let formatDataList = []
	for (let i in dbs) {
		let itemb = dbs[i]
		if ( formatDataList.length == 0) {
			let data = {
				value: itemb.cluster_id,
				label: itemb.cluster_name,
				children: [
					{
						value: itemb.env,
						label: itemb.env,
						children: [
							{
								value: itemb.id,
								label: itemb.name,
							},
						]
					},
				]
			}
			formatDataList.push(data)
		} else {
			let tag = 0
			for (let j in formatDataList) {
				let itema = formatDataList[j]
				if (itemb.cluster_name == itema.label) {
					let env_children = itema.children
					if (env_children.length == 2) {
						for (let m in env_children) {
							let env_item = env_children[m]
							if (env_item.value == itemb.env) {
								let host = {value:itemb.id, label:itemb.name}
								env_item.children.push(host)
								break
							}
						}

					} else if (env_children.length == 1) {
						let env_children0 = env_children[0]
						if (env_children0.value == itemb.env) {
							let host = {value:itemb.id, label:itemb.name}
							env_children0.children.push(host)
						} else {
							let data = 			
								{
									value: itemb.env,
									label: itemb.env,
									children: [
										{
											value: itemb.id,
											label: itemb.name,
										},
									]
								}
							env_children.push(data)
						}
					}
					tag = 1
					break
				} 
			}	
			if (tag == 0) {
					let data = 	{
						value: itemb.cluster_id,
						label: itemb.cluster_name,
						children: [
							{
								value: itemb.env,
								label: itemb.env,
								children: [
									{
										value: itemb.id,
										label: itemb.name,
									},
								]
							},
						]
					}
					formatDataList.push(data)
			}

		}

	}
	return formatDataList
}