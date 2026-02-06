import React, { useState } from 'react'
import { PredictionInput, PredictionResult } from '../types'
import { API_BASE_URL } from '../constants'

export default function PredictionForm(){
  const [input, setInput] = useState<PredictionInput>({hour:12, day_of_week:3, appliance_id:'fridge_207'})
  const [result, setResult] = useState<PredictionResult | null>(null)
  const [loading, setLoading] = useState(false)

  async function submit(e:React.FormEvent){
    e.preventDefault()
    setLoading(true)
    try{
      const res = await fetch(`${API_BASE_URL}/predict`,{
        method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(input)
      })
      const data = await res.json()
      setResult(data)
    }catch(err){
      console.error(err)
      setResult(null)
    }finally{setLoading(false)}
  }

  return (
    <div>
      <form onSubmit={submit}>
        <label>Hour: <input type="number" value={input.hour} onChange={e=>setInput({...input,hour:Number(e.target.value)})} /></label>
        <label>Day: <input type="number" value={input.day_of_week} onChange={e=>setInput({...input,day_of_week: Number(e.target.value)})} /></label>
        <label>Appliance ID: <input value={input.appliance_id} onChange={e=>setInput({...input,appliance_id:e.target.value})} /></label>
        <button type="submit" disabled={loading}>{loading? 'Predicting...' : 'Predict'}</button>
      </form>
      {result && (
        <div className="result">
          <h3>Prediction</h3>
          <div>Predicted disparity (W): {result.predicted_disparity_w}</div>
          {result.confidence!=null && <div>Confidence: {result.confidence}%</div>}
        </div>
      )}
    </div>
  )
}
