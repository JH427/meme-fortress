const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const tileSize = 32;

// Draw a single tile
function drawTile(x, y, type) {
    if (type === "empty") ctx.fillStyle = "#222";
    else if (type === "mine") ctx.fillStyle = "#444";
    else if (type === "structure") ctx.fillStyle = "#0f0";
    else if (type === "cringe_mine") ctx.fillStyle = "#ff69b4";
    else if (type === "copium_field") ctx.fillStyle = "#00ffff";
    else ctx.fillStyle = "#f00";

    ctx.fillRect(x * tileSize, y * tileSize, tileSize, tileSize);
}


// Fetch and draw the world
async function loadWorld() {
    const res = await fetch("http://localhost:8000/world");
    const world = await res.json();
    drawWorld(world);
}

function drawWorld(world) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    world.forEach(tile => drawTile(tile.x, tile.y, tile.type));
    animateAgents(); // draw smooth agents over tiles
}

// WebSocket messaging
const socket = new WebSocket("ws://localhost:8000/ws");

function send() {
    const input = document.getElementById("cmd");
    socket.send(JSON.stringify({ command: input.value }));
    input.value = "";
}

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const log = document.getElementById("log");
    log.textContent += `${data.agent}: ${data.response}\n`;

    loadWorld(); // ⬅️ Redraw the map after each command
};

// Initial map draw on page load
loadWorld();

canvas.addEventListener("click", (event) => {
    const rect = canvas.getBoundingClientRect();
    const x = Math.floor((event.clientX - rect.left) / tileSize);
    const y = Math.floor((event.clientY - rect.top) / tileSize);

    const tileType = prompt("What do you want to build here? (structure, cringe_mine, copium_field)");
    if (!tileType) return;

    socket.send(JSON.stringify({ command: `build ${tileType} at ${x},${y}` }));
});

function getAgentQuote(trait) {
    const lines = {
        "chaotic": ["lmao", "oops", "memes > orders"],
        "clout chaser": ["follow me", "#AIhustle", "where's the copium?"],
        "doomer": ["it's all pointless", "copium... please", "we're all dying"]
    };
    const pool = lines[trait] || ["..."];
    return pool[Math.floor(Math.random() * pool.length)];
}


let agentSprites = {}; // keeps track of previous and target positions

async function updateAgentTargets() {
    const res = await fetch("http://localhost:8000/agents");
    const agents = await res.json();

    agents.forEach(agent => {
        const id = agent.name;

        if (!agentSprites[id]) {
            agentSprites[id] = {
                x: agent.x,
                y: agent.y,
                targetX: agent.x,
                targetY: agent.y,
                say: getAgentQuote(agent.trait)
            };
        } else {
            agentSprites[id].targetX = agent.x;
            agentSprites[id].targetY = agent.y;

            // occasionally update speech bubble (e.g., every 1 in 4 updates)
            if (Math.random() < 0.25) {
                agentSprites[id].say = getAgentQuote(agent.trait);
            }
        }
    });
}


function animateAgents() {
    const crineImg = document.getElementById("crineEmoji");

    for (const id in agentSprites) {
        const a = agentSprites[id];

        // Interpolate smoothly toward target
        a.x += (a.targetX - a.x) * 0.1;
        a.y += (a.targetY - a.y) * 0.1;

        if (Math.abs(a.x - a.targetX) < 0.01) a.x = a.targetX;
        if (Math.abs(a.y - a.targetY) < 0.01) a.y = a.targetY;

        ctx.drawImage(
            crineImg,
            a.x * tileSize + 4,
            a.y * tileSize + 4,
            tileSize - 8,
            tileSize - 8
        );

        ctx.font = "10px Arial";
        ctx.fillStyle = "white";
        ctx.fillText(a.say, a.x * tileSize + 2, a.y * tileSize - 4);
    }
}


// Re-fetch agent targets every 2 seconds
setInterval(() => {
    updateAgentTargets();  // ⬅️ not loadWorld anymore
}, 2000);

function gameLoop() {
    loadWorld(); // redraw everything with interpolated agent positions
    requestAnimationFrame(gameLoop);
}
gameLoop();



