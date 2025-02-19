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
    
    # First draw what's behind the door
    if state == 'car':
        # Draw car
        draw.rectangle([0, 0, width, height], fill='#2C3E50')  # Background
        # Car body
        draw.rectangle([40, 120, 160, 170], fill='#E74C3C')
        draw.polygon([(60, 120), (140, 120), (130, 80), (70, 80)], fill='#E74C3C')
        # Windows
        draw.polygon([(75, 85), (125, 85), (115, 115), (85, 115)], fill='#85C1E9')
        # Wheels
        draw.ellipse([50, 150, 80, 180], fill='#2C3E50', outline='white', width=2)
        draw.ellipse([120, 150, 150, 180], fill='#2C3E50', outline='white', width=2)
        draw.text((100, 280), "CAR!", fill='white', anchor="ms")
    elif state == 'goat' or opening:
        # Draw goat
        draw.rectangle([0, 0, width, height], fill='#27AE60')  # Green background
        # Goat body
        draw.ellipse([60, 120, 140, 180], fill='#95A5A6')
        draw.ellipse([120, 90, 150, 120], fill='#95A5A6')  # Head
        # Legs
        draw.rectangle([70, 170, 85, 220], fill='#95A5A6')
        draw.rectangle([115, 170, 130, 220], fill='#95A5A6')
        draw.text((100, 280), "GOAT", fill='white', anchor="ms")
    
    # Then draw the door (if closed or partially open)
    if state == 'closed' or opening:
        # Door frame always visible
        draw.rectangle([15, 15, 185, 285], fill='#654321', outline='#463217', width=3)
        
        if opening:
            # Draw partially open door
            door_width = int(180 * 0.3)  # Door is 30% visible (70% open)
            door_color = '#27AE60' if selected else '#8B4513'
            # Draw the door on the left side
            draw.rectangle([20, 20, 20 + door_width, 280], fill=door_color, outline='#654321', width=2)
            # Draw handle if door is wide enough
            if door_width > 30:
                draw.ellipse([door_width - 30, 140, door_width - 10, 160], fill='#FFD700')
        else:
            # Draw fully closed door
            door_color = '#27AE60' if selected else '#8B4513'
            draw.rectangle([20, 20, 180, 280], fill=door_color, outline='#654321', width=2)
            draw.rectangle([35, 35, 165, 135], fill=door_color, outline='#654321', width=2)
            draw.rectangle([35, 165, 165, 265], fill=door_color, outline='#654321', width=2)
            draw.ellipse([150, 140, 170, 160], fill='#FFD700')  # Handle
            draw.text((100, 280), f"Door {door_num + 1}", fill='white', anchor="ms")
    
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

def process_choice(final_choice, is_switch):
    """Process the player's final choice and update statistics"""
    # Update the chosen door to the final choice
    st.session_state.chosen_door = final_choice
    
    if is_switch:
        # Player switched
        st.session_state.stats_switch['games'] += 1
        if final_choice == st.session_state.car_position:
            st.session_state.stats_switch['wins'] += 1
    else:
        # Player stayed
        st.session_state.stats_stay['games'] += 1
        if final_choice == st.session_state.car_position:
            st.session_state.stats_stay['wins'] += 1
    
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
                            process_choice(i, False)  # Stay with initial choice
                        else:  # Always switch
                            # Find the remaining unopened door
                            final_choice = [x for x in range(3) 
                                          if x != i and x != st.session_state.revealed_door][0]
                            process_choice(final_choice, True)  # Switch to the other door
                
                elif st.session_state.game_state == 'deciding':
                    # For manual choice, determine if player switched
                    is_switch = (i != st.session_state.chosen_door)
                    process_choice(i, is_switch)
            
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
                # Setup game
                car_pos = random.randint(0, 2)
                first_choice = random.randint(0, 2)
                
                # Find possible goat doors to reveal
                possible_reveals = [i for i in range(3) 
                                  if i != first_choice and i != car_pos]
                if not possible_reveals:
                    possible_reveals = [i for i in range(3) 
                                      if i != first_choice]
                    if car_pos in possible_reveals:
                        possible_reveals.remove(car_pos)
                
                revealed_door = random.choice(possible_reveals)
                
                # Simulate staying
                st.session_state.stats_stay['games'] += 1
                if first_choice == car_pos:
                    st.session_state.stats_stay['wins'] += 1
                
                # Simulate switching
                st.session_state.stats_switch['games'] += 1
                # Switch to the door that's neither the first choice nor the revealed door
                final_choice = [i for i in range(3) 
                              if i != first_choice and i != revealed_door][0]
                if final_choice == car_pos:
                    st.session_state.stats_switch['wins'] += 1

    # Add sound effects (if browser supports it)
    if st.session_state.game_state == 'finished':
        st.markdown("""
            <audio autoplay>
                <source src="data:audio/wav;base64,{encoded_sound}" type="audio/wav">
            </audio>
        """, unsafe_allow_html=True)

    # Replace the line graph with a donut chart
    if st.session_state.stats_stay['games'] > 0 or st.session_state.stats_switch['games'] > 0:
        st.header("Win Percentages")
        
        fig = go.Figure()
        
        # Calculate percentages
        stay_pct = (st.session_state.stats_stay['wins'] / st.session_state.stats_stay['games'] * 100 
                   if st.session_state.stats_stay['games'] > 0 else 0)
        switch_pct = (st.session_state.stats_switch['wins'] / st.session_state.stats_switch['games'] * 100 
                     if st.session_state.stats_switch['games'] > 0 else 0)

        # Add donut charts side by side
        fig = go.Figure(data=[
            # Stay strategy donut
            go.Pie(
                values=[stay_pct, 100-stay_pct],
                labels=['Wins', 'Losses'],
                name="Stay Strategy",
                domain={'x': [0, 0.45]},
                hole=0.7,
                marker_colors=['#2ecc71', '#e74c3c'],
                title="Stay Strategy"
            ),
            # Switch strategy donut
            go.Pie(
                values=[switch_pct, 100-switch_pct],
                labels=['Wins', 'Losses'],
                name="Switch Strategy",
                domain={'x': [0.55, 1]},
                hole=0.7,
                marker_colors=['#2ecc71', '#e74c3c'],
                title="Switch Strategy"
            )
        ])
        
        # Update layout
        fig.update_layout(
            showlegend=True,
            annotations=[
                # Stay percentage in center
                dict(
                    text=f'{stay_pct:.1f}%',
                    x=0.225, y=0.5,
                    font_size=24,
                    showarrow=False
                ),
                # Switch percentage in center
                dict(
                    text=f'{switch_pct:.1f}%',
                    x=0.775, y=0.5,
                    font_size=24,
                    showarrow=False
                )
            ],
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main() 