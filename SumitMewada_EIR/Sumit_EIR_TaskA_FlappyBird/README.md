# 🐦 Flappy Bird Pro - Enhanced Edition

A modern, feature-rich implementation of the classic Flappy Bird game with enhanced graphics, multiple difficulty levels, power-ups, and mobile support.

## ✨ Features

### 🎮 Game Mechanics
- **Multiple Difficulty Levels**: Easy, Normal, Hard, and Extreme modes
- **Power-ups**: Shield power-up for temporary invincibility
- **Combo System**: Build combos by passing through pipes consecutively
- **Level Progression**: Automatic level advancement based on score
- **High Score Tracking**: Persistent local storage of best scores

### 🎨 Visual Enhancements
- **Animated Background**: Dynamic sky gradient with moving clouds
- **Particle Effects**: Visual feedback for jumps, dives, and collisions
- **Bird Trail Effect**: Smooth trailing animation behind the bird
- **Gradient Pipes**: Colorful pipes with varied hues
- **Responsive Design**: Optimized for both desktop and mobile devices

### 🎯 Controls
- **Desktop**: 
  - `↑` / `W` - Jump
  - `↓` / `S` - Dive (faster descent)
  - `P` - Pause/Resume
  - `R` - Restart (return to menu)
  - `ESC` - Return to main menu
- **Mobile**: 
  - Tap screen to jump
  - Mobile menu button for game controls
  - Haptic feedback support

### 📱 Mobile Optimization
- Full-screen responsive gameplay
- Touch controls with visual feedback
- Optimized UI scaling for different screen sizes
- Orientation change support

## 🚀 Getting Started

### Prerequisites
- Modern web browser with HTML5 Canvas support
- No additional dependencies required

### Installation
1. Clone or download the project files
2. Open `index.html` in your web browser
3. Start playing!

### File Structure
```
Sumit_EIR_TaskA_FlappyBird/
├── index.html          # Complete game implementation
└── README.md          # This file
```

## 🎯 How to Play

1. **Start the Game**: Select your preferred difficulty level and click "START GAME"
2. **Control the Bird**: Use keyboard controls (desktop) or tap (mobile) to make the bird fly
3. **Avoid Obstacles**: Navigate through the gaps between pipes
4. **Collect Power-ups**: Grab shield power-ups for temporary invincibility
5. **Build Combos**: Pass through multiple pipes consecutively for bonus points
6. **Beat Your High Score**: Try to achieve the highest score possible!

## 🎮 Difficulty Levels

| Difficulty | Gravity | Pipe Speed | Pipe Gap | Spawn Rate |
|------------|---------|------------|----------|------------|
| **Easy** 🟢 | 0.4 | 2 | 200px | Slow |
| **Normal** 🟡 | 0.5 | 3 | 170px | Medium |
| **Hard** 🔴 | 0.6 | 4 | 150px | Fast |
| **Extreme** 💀 | 0.7 | 5 | 130px | Very Fast |

## 🛡️ Power-ups

- **Shield** 🛡️: Provides temporary invincibility, allowing you to pass through pipes without dying
- Duration: ~3 seconds
- Spawn Rate: 15% chance per pipe set

## 🏆 Scoring System

- **+1 Point**: Successfully passing through a pipe gap
- **Combo Multiplier**: Consecutive successful passes build combo streaks
- **Level Progression**: Every 5 points advances to the next level
- **High Score**: Automatically saved to browser's local storage

## 🔧 Technical Details

### Technologies Used
- **HTML5 Canvas**: For game rendering and animations
- **Vanilla JavaScript**: Game logic and mechanics
- **CSS3**: Styling and responsive design
- **Local Storage**: High score persistence

### Performance Features
- Optimized particle system
- Efficient collision detection
- Smooth 60 FPS gameplay
- Memory-conscious object pooling

### Browser Compatibility
- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🎨 Customization

The game is built with modular code that allows for easy customization:

- **Difficulty Settings**: Modify the `difficulties` object to adjust game parameters
- **Visual Themes**: Update CSS variables and canvas drawing functions
- **Power-up Types**: Extend the power-up system with new abilities
- **Scoring Rules**: Adjust point values and combo mechanics

## 📱 Mobile Features

- **Touch Controls**: Responsive tap-to-jump mechanics
- **Visual Feedback**: Tap indicators show where touches are registered
- **Haptic Feedback**: Vibration support on compatible devices
- **Adaptive UI**: Interface elements scale appropriately for mobile screens
- **Performance Optimization**: Reduced particle counts and effects for smoother mobile gameplay

## 🐛 Known Issues

- None currently reported

## 🤝 Contributing

This is a single-file implementation perfect for learning and experimentation. Feel free to:
- Add new features
- Improve graphics and animations
- Optimize performance
- Add new power-up types
- Create different themes

## 📄 License

This project is open source and available under the MIT License.

## 🎉 Credits

- Inspired by the original Flappy Bird by Dong Nguyen
- Enhanced with modern web technologies and features
- Built for educational and entertainment purposes

---

**Enjoy the game and happy flying! 🐦✨**
