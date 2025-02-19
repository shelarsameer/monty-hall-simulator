import streamlit as st
import random
from PIL import Image, ImageDraw
import os
import time
import base64
from io import BytesIO
from create_images import save_images
import plotly.graph_objects as go

# Initialize session state
if 'stats_switch' not in st.session_state:
    st.session_state.stats_switch = {'wins': 0, 'games': 0}
if 'stats_stay' not in st.session_state:
    st.session_state.stats_stay = {'wins': 0, 'games': 0}
if 'game_state' not in st.session_state:
    st.session_state.game_state = 'choosing'
if 'car_position' not in st.session_state:
    st.session_state.car_position = random.randint(0, 2)
if 'chosen_door' not in st.session_state:
    st.session_state.chosen_door = None
if 'revealed_door' not in st.session_state:
    st.session_state.revealed_door = None

def create_door_image(door_num, state='closed', selected=False, opening=False):
    width, height = 200, 300
    img = Image.new('RGB', (width, height), '#34495E')
    draw = ImageDraw.Draw(img)
    
    if state == 'closed' and not opening:
        # Draw closed door
        color = '#27AE60' if selected else '#8B4513'
        # Door frame
        draw.rectangle([15, 15, 185, 285], fill='#654321', outline='#463217', width=3)
        # Door
        draw.rectangle([20, 20, 180, 280], fill=color, outline='#654321', width=2)
        # Decorative panels
        draw.rectangle([35, 35, 165, 135], fill=color, outline='#654321', width=2)
        draw.rectangle([35, 165, 165, 265], fill=color, outline='#654321', width=2)
        # Door handle
        draw.ellipse([150, 140, 170, 160], fill='#FFD700')
        # Door number
        draw.text((100, 280), f"Door {door_num + 1}", fill='white', anchor="ms")
    elif state == 'car' or (state == 'closed' and opening):
        # Draw car or background for opening animation
        draw.rectangle([0, 0, width, height], fill='#2C3E50')  # Background
        if state == 'car':
            # Car body
            draw.rectangle([40, 120, 160, 170], fill='#E74C3C')
            draw.polygon([(60, 120), (140, 120), (130, 80), (70, 80)], fill='#E74C3C')
            # Windows
            draw.polygon([(75, 85), (125, 85), (115, 115), (85, 115)], fill='#85C1E9')
            # Wheels
            draw.ellipse([50, 150, 80, 180], fill='#2C3E50', outline='white', width=2)
            draw.ellipse([120, 150, 150, 180], fill='#2C3E50', outline='white', width=2)
            draw.text((100, 280), "CAR!", fill='white', anchor="ms")
    else:  # goat or opening to goat
        draw.rectangle([0, 0, width, height], fill='#27AE60')  # Green background
        # Goat body
        draw.ellipse([60, 120, 140, 180], fill='#95A5A6')
        draw.ellipse([120, 90, 150, 120], fill='#95A5A6')  # Head
        # Legs
        draw.rectangle([70, 170, 85, 220], fill='#95A5A6')
        draw.rectangle([115, 170, 130, 220], fill='#95A5A6')
        draw.text((100, 280), "GOAT", fill='white', anchor="ms")
    
    # Draw opening door animation if needed
    if opening:
        door_width = int(180 * 0.3)  # Show door mostly open
        door_color = '#27AE60' if selected else '#8B4513'
        
        # Door frame
        draw.rectangle([15, 15, 185, 285], fill='#654321', outline='#463217', width=3)
        # Animated door
        draw.rectangle([20, 20, 20 + door_width, 280], fill=door_color, outline='#654321', width=2)
        if door_width > 30:  # Only draw handle if door is wide enough
            draw.ellipse([door_width - 30, 140, door_width - 10, 160], fill='#FFD700')
    
    return img

def reset_game():
    st.session_state.car_position = random.randint(0, 2)
    st.session_state.chosen_door = None
    st.session_state.revealed_door = None
    st.session_state.game_state = 'choosing'

def reveal_goat():
    """Reveal a goat behind one of the non-chosen doors"""
    possible_reveals = []
    
    # Find doors that can be revealed (not chosen and has a goat)
    for i in range(3):
        if i != st.session_state.chosen_door and i != st.session_state.car_position:
            possible_reveals.append(i)
    
    # If we have multiple options, randomly choose one
    st.session_state.revealed_door = random.choice(possible_reveals)
    st.session_state.game_state = 'deciding'

def process_choice(final_choice):
    """Process the player's final choice and update statistics"""
    if final_choice == st.session_state.chosen_door:
        # Player stayed
        st.session_state.stats_stay['games'] += 1
        if final_choice == st.session_state.car_position:
            st.session_state.stats_stay['wins'] += 1
    else:
        # Player switched
        st.session_state.stats_switch['games'] += 1
        if final_choice == st.session_state.car_position:
            st.session_state.stats_switch['wins'] += 1
    st.session_state.game_state = 'finished'

def create_monty_hall(position=None):
    """Create Monty Hall host character"""
    width, height = 100, 200
    img = Image.new('RGB', (width, height), '#34495E')
    draw = ImageDraw.Draw(img)
    
    # Body
    draw.ellipse([30, 60, 70, 100], fill='#2E4053')  # Head
    draw.rectangle([45, 100, 55, 150], fill='#E74C3C')  # Body
    
    # Bow tie
    draw.polygon([(40, 110), (60, 110), (50, 115)], fill='#F1C40F')
    
    # Arms - position them based on whether he's pointing
    if position is not None:
        # Pointing arm
        if position == 0:
            draw.line([50, 120, 20, 140], fill='#E74C3C', width=5)
        elif position == 1:
            draw.line([50, 120, 50, 140], fill='#E74C3C', width=5)
        else:
            draw.line([50, 120, 80, 140], fill='#E74C3C', width=5)
    else:
        # Normal arms
        draw.line([50, 120, 30, 140], fill='#E74C3C', width=5)
        draw.line([50, 120, 70, 140], fill='#E74C3C', width=5)
    
    return img

def get_image_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

def create_clickable_image(img, key, disabled=False):
    img_str = get_image_base64(img)
    
    # Create HTML for clickable image with improved styling
    html = f'''
        <div style="cursor: {'default' if disabled else 'pointer'}; 
                    transition: transform 0.2s;"
             onmouseover="this.style.transform='scale(1.02)'"
             onmouseout="this.style.transform='scale(1)'"
             onclick="
            if (!{str(disabled).lower()}) {{
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    key: '{key}',
                    value: true
                }}, '*');
            }}">
            <img src="data:image/png;base64,{img_str}" 
                 style="width: 100%; 
                        {'opacity: 0.5;' if disabled else ''};
                        border-radius: 10px;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        </div>
    '''
    
    # Use streamlit components to create clickable element
    clicked = st.components.v1.html(html, height=320)
    return clicked

def create_door_animation(is_selected=False, content=None, animation_progress=0):
    """Create door with opening animation"""
    width, height = 200, 300
    img = Image.new('RGB', (width, height), '#34495E')
    draw = ImageDraw.Draw(img)
    
    # Draw background (what's behind the door)
    if content == "car":
        # Draw car (enhanced version)
        draw.rectangle([0, 0, width, height], fill='#2C3E50')
        draw.rectangle([30, 120, 170, 180], fill='#E74C3C')
        draw.polygon([(50, 120), (150, 120), (130, 80), (70, 80)], fill='#E74C3C')
        draw.polygon([(75, 85), (125, 85), (115, 115), (85, 115)], fill='#85C1E9')
        draw.ellipse([45, 160, 85, 200], fill='#2C3E50', outline='#95A5A6', width=3)
        draw.ellipse([115, 160, 155, 200], fill='#2C3E50', outline='#95A5A6', width=3)
        draw.ellipse([35, 140, 45, 150], fill='#F1C40F')
    elif content == "goat":
        # Draw goat (enhanced version)
        draw.rectangle([0, 0, width, height], fill='#27AE60')
        draw.ellipse([50, 120, 150, 190], fill='#95A5A6')
        draw.ellipse([130, 80, 170, 120], fill='#95A5A6')
        draw.line([150, 85, 160, 65], fill='#7F8C8D', width=3)
        draw.line([160, 85, 170, 65], fill='#7F8C8D', width=3)
        draw.rectangle([70, 180, 85, 240], fill='#95A5A6')
        draw.rectangle([115, 180, 130, 240], fill='#95A5A6')
        draw.ellipse([145, 90, 155, 100], fill='#2C3E50')
        draw.rectangle([0, 240, width, height], fill='#27AE60')
    
    # Draw door with animation
    if animation_progress < 1:
        door_width = int(180 * (1 - animation_progress))
        door_color = '#27AE60' if is_selected else '#8B4513'
        
        # Door frame
        draw.rectangle([15, 15, 185, 285], fill='#654321', outline='#463217', width=3)
        # Animated door
        draw.rectangle([20, 20, 20 + door_width, 280], fill=door_color, outline='#654321', width=2)
        if door_width > 100:  # Only draw handle if door is wide enough
            draw.ellipse([door_width - 30, 140, door_width - 10, 160], fill='#FFD700')
    
    return img

def main():
    st.set_page_config(page_title="Monty Hall Simulator", layout="wide")
    
    # Add custom CSS
    st.markdown("""
        <style>
        .stButton button {
            width: 100%;
            font-size: 18px;
            padding: 10px;
        }
        .stRadio [role='radiogroup'] {
            display: flex;
            justify-content: center;
            gap: 20px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🚪 Monty Hall Problem Simulator")
    st.markdown("""
    ### The Game Rules:
    1. There are 3 doors, behind one is a car 🚗, behind the others are goats 🐐
    2. Pick a door
    3. One of the other doors with a goat will be revealed
    4. You can stay with your choice or switch to the remaining door
    """)

    # Strategy selection
    strategy = st.radio(
        "Select your strategy:",
        ['Choose manually', 'Always stay', 'Always switch'],
        horizontal=True
    )

    # Display doors
    cols = st.columns(3)
    for i in range(3):
        with cols[i]:
            # Determine door state and content
            state = 'closed'
            opening = False
            
            if st.session_state.game_state == 'finished':
                state = 'car' if i == st.session_state.car_position else 'goat'
            elif st.session_state.game_state == 'deciding':
                if i == st.session_state.revealed_door:
                    state = 'goat'
                    opening = True  # Show opening animation for revealed goat
            
            # Create door image
            door_img = create_door_image(
                i, 
                state=state,
                selected=(i == st.session_state.chosen_door),
                opening=opening
            )
            
            # Door button
            disabled = (st.session_state.game_state == 'finished' or 
                      (st.session_state.game_state == 'deciding' and i == st.session_state.revealed_door))
            
            if st.button(f"Select Door {i+1}", key=f"door_{i}", disabled=disabled):
                if st.session_state.game_state == 'choosing':
                    st.session_state.chosen_door = i
                    reveal_goat()  # Immediately reveal a goat door after first choice
                    
                    if strategy != 'Choose manually':
                        if strategy == 'Always stay':
                            process_choice(i)
                        else:  # Always switch
                            final_choice = [x for x in range(3) 
                                          if x != i and x != st.session_state.revealed_door][0]
                            process_choice(final_choice)
                
                elif st.session_state.game_state == 'deciding':
                    process_choice(i)  # Process final choice and reveal all doors
            
            st.image(door_img)

    # Game status
    if st.session_state.game_state == 'choosing':
        st.info("Choose a door!")
    elif st.session_state.game_state == 'deciding':
        st.warning(f"Door {st.session_state.revealed_door + 1} has been opened showing a goat! Would you like to switch your choice?")
    elif st.session_state.game_state == 'finished':
        won = st.session_state.chosen_door == st.session_state.car_position
        result = "Won! 🎉" if won else "Lost! 😢"
        car_door = st.session_state.car_position + 1
        st.success(f"Game Over - You {result} The car was behind Door {car_door}!")

    # Statistics
    st.header("Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        stay_games = st.session_state.stats_stay['games']
        stay_wins = st.session_state.stats_stay['wins']
        stay_pct = (stay_wins / stay_games * 100) if stay_games > 0 else 0
        st.metric("Stay Strategy", f"{stay_pct:.1f}%", 
                 f"Wins: {stay_wins}/{stay_games}")

    with col2:
        switch_games = st.session_state.stats_switch['games']
        switch_wins = st.session_state.stats_switch['wins']
        switch_pct = (switch_wins / switch_games * 100) if switch_games > 0 else 0
        st.metric("Switch Strategy", f"{switch_pct:.1f}%",
                 f"Wins: {switch_wins}/{switch_games}")

    # Control buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("New Game"):
            reset_game()
    
    with col2:
        if st.button("Auto Simulate (100 games)"):
            for _ in range(100):
                # Simulate staying
                car_pos = random.randint(0, 2)
                first_choice = random.randint(0, 2)
                # For staying, just check if initial choice was correct
                st.session_state.stats_stay['games'] += 1
                if first_choice == car_pos:
                    st.session_state.stats_stay['wins'] += 1
                
                # Simulate switching
                car_pos = random.randint(0, 2)
                first_choice = random.randint(0, 2)
                # Get doors we could reveal (not chosen and not car)
                possible_reveals = [i for i in range(3) 
                                  if i != first_choice and i != car_pos]
                # Host reveals one of these doors
                revealed_door = random.choice(possible_reveals)
                # Player switches to the remaining door
                final_choice = [i for i in range(3) 
                               if i != first_choice and i != revealed_door][0]
                
                st.session_state.stats_switch['games'] += 1
                if final_choice == car_pos:
                    st.session_state.stats_switch['wins'] += 1

    # Add sound effects (if browser supports it)
    if st.session_state.game_state == 'finished':
        st.markdown("""
            <audio autoplay>
                <source src="data:audio/wav;base64,{encoded_sound}" type="audio/wav">
            </audio>
        """, unsafe_allow_html=True)

    # Add a plot showing win probabilities over time
    if st.session_state.stats_stay['games'] > 0 or st.session_state.stats_switch['games'] > 0:
        st.header("Win Probability Over Time")
        
        fig = go.Figure()
        
        # Add stay strategy line
        stay_prob = (st.session_state.stats_stay['wins'] / st.session_state.stats_stay['games'] * 100 
                    if st.session_state.stats_stay['games'] > 0 else 0)
        fig.add_trace(go.Scatter(x=[0, st.session_state.stats_stay['games']], 
                                y=[0, stay_prob],
                                name="Stay Strategy",
                                line=dict(color="#1f77b4")))
        
        # Add switch strategy line
        switch_prob = (st.session_state.stats_switch['wins'] / st.session_state.stats_switch['games'] * 100 
                      if st.session_state.stats_switch['games'] > 0 else 0)
        fig.add_trace(go.Scatter(x=[0, st.session_state.stats_switch['games']], 
                                y=[0, switch_prob],
                                name="Switch Strategy",
                                line=dict(color="#ff7f0e")))
        
        # Add theoretical probabilities
        fig.add_hline(y=33.33, line_dash="dash", annotation_text="1/3 probability")
        fig.add_hline(y=66.67, line_dash="dash", annotation_text="2/3 probability")
        
        fig.update_layout(
            title="Win Probability Over Number of Games",
            xaxis_title="Number of Games",
            yaxis_title="Win Probability (%)",
            yaxis_range=[0, 100]
        )
        
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main() 