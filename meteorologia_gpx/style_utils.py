import streamlit as st

class StyleManager:
    """Manages custom CSS injection for a premium Look & Feel."""

    @staticmethod
    def inject_css():
        """Injects custom CSS into the Streamlit app."""
        st.markdown(
            """
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

            html, body, [class*="css"] {
                font-family: 'Inter', sans-serif;
            }

            /* Glassmorphism Sidebar */
            [data-testid="stSidebar"] {
                background-color: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
                border-right: 1px solid rgba(255, 255, 255, 0.1);
            }

            /* Custom Cards for Weather */
            .weather-card {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                margin-bottom: 20px;
                transition: transform 0.3s ease;
            }

            .weather-card:hover {
                transform: translateY(-5px);
                border-color: rgba(0, 150, 255, 0.5);
            }

            /* Gradient Text */
            .gradient-text {
                background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-weight: 700;
            }

            /* Style standard buttons */
            .stButton>button {
                border-radius: 10px;
                background: linear-gradient(45deg, #2b5876 0%, #4e4376 100%);
                color: white;
                border: none;
                padding: 10px 24px;
                transition: all 0.3s ease;
            }

            .stButton>button:hover {
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                transform: scale(1.02);
            }

            /* Metrics Styling */
            [data-testid="stMetricValue"] {
                font-size: 1.8rem;
                font-weight: 700;
                color: #00C9FF;
            }

            /* Header */
            .main-header {
                font-size: 2.5rem;
                font-weight: 800;
                margin-bottom: 1rem;
                text-align: center;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

    @staticmethod
    def render_header(title, subtitle):
        """Renders a custom header with styled HTML."""
        st.markdown(
            f"""
            <div class="main-header">
                <span class="gradient-text">{title}</span>
            </div>
            <p style="text-align: center; color: #aaa; margin-bottom: 2rem;">{subtitle}</p>
            """,
            unsafe_allow_html=True
        )

    @staticmethod
    def render_weather_summary(max_temp, min_temp, max_rain):
        """Renders stylized weather cards."""
        cols = st.columns(3)
        
        with cols[0]:
            st.markdown(
                f"""
                <div class="weather-card">
                    <div style="font-size: 0.9rem; color: #888;">Temp. Máxima</div>
                    <div style="font-size: 2rem; font-weight: 700; color: #ff4b4b;">{max_temp}°C</div>
                </div>
                """, unsafe_allow_html=True
            )
        
        with cols[1]:
            st.markdown(
                f"""
                <div class="weather-card">
                    <div style="font-size: 0.9rem; color: #888;">Temp. Mínima</div>
                    <div style="font-size: 2rem; font-weight: 700; color: #00d2ff;">{min_temp}°C</div>
                </div>
                """, unsafe_allow_html=True
            )

        with cols[2]:
            color = "#00ffa3" if max_rain == 0 else "#ffcc00"
            icon = "☀️" if max_rain == 0 else "🌧️"
            text = "Sin Lluvia" if max_rain == 0 else f"{max_rain}mm Máx"
            st.markdown(
                f"""
                <div class="weather-card">
                    <div style="font-size: 0.9rem; color: #888;">Precipitación</div>
                    <div style="font-size: 2rem; font-weight: 700; color: {color};">{icon} {text}</div>
                </div>
                """, unsafe_allow_html=True
            )
