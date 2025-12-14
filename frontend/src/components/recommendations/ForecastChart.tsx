import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Forecast } from '../../types/forecast';
import './ForecastChart.css';

interface ForecastChartProps {
  forecasts: Forecast[];
}

const ForecastChart: React.FC<ForecastChartProps> = ({ forecasts }) => {
  if (!forecasts || forecasts.length === 0) {
    return (
      <div className="forecast-chart-empty">
        <p>No forecast data available for chart.</p>
      </div>
    );
  }

  // Prepare data for chart
  const chartData = forecasts.map((forecast) => ({
    date: new Date(forecast.forecast_date).toLocaleDateString(),
    predicted: forecast.predicted_demand,
    lower: forecast.confidence_lower || forecast.predicted_demand * 0.9,
    upper: forecast.confidence_upper || forecast.predicted_demand * 1.1,
    horizon: `${forecast.forecast_horizon_days}d`,
  }));

  return (
    <div className="forecast-chart">
      <h3>Demand Forecast</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="predicted"
            stroke="#667eea"
            strokeWidth={2}
            name="Predicted Demand"
          />
          <Line
            type="monotone"
            dataKey="lower"
            stroke="#ef4444"
            strokeDasharray="5 5"
            name="Lower Bound"
          />
          <Line
            type="monotone"
            dataKey="upper"
            stroke="#10b981"
            strokeDasharray="5 5"
            name="Upper Bound"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ForecastChart;
