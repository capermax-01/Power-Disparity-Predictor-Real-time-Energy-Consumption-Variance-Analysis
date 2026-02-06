import React, { useEffect, useState } from 'react'

export default function Dashboard(){
  const [info, setInfo] = useState<any>(null)
  useEffect(()=>{
    fetch('/api/model/info').then(r=>r.json()).then(setInfo).catch(()=>setInfo(null))
  },[])
  return (
    <div>
      <h2>Model Dashboard</h2>
      {info ? <pre>{JSON.stringify(info, null, 2)}</pre> : <p>No model info available.</p>}
    </div>
  )
}
