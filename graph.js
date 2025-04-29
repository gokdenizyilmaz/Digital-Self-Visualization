let allData = [];
let Graph = null;

function initGraph(data) {
  if (Graph) {
    Graph.graphData({ nodes: [], links: [] }); // Temizle
  }

  const nodes = [];
  const links = [];

  data.forEach((conv, idx) => {
    nodes.push({
      id: `conv_${idx}`,
      label: conv.title,
      messages: conv.messages,  // Mesajları ekliyoruz
      group: conv.month
    });
  });

  // Bağlantıları (links) oluşturuyoruz
  for (let i = 0; i < data.length; i++) {
    for (let j = i + 1; j < data.length; j++) {
      const shared = data[i].title.toLowerCase().split(/\s+/)
        .filter(word => data[j].title.toLowerCase().includes(word));
      if (shared.length > 0) {
        links.push({
          source: `conv_${i}`,
          target: `conv_${j}`,
          value: shared.length
        });
      }
    }
  }

  if (!Graph) {
    Graph = ForceGraph3D()(document.getElementById('graph'))
      .nodeLabel(node => node.label)
      .nodeAutoColorBy('group')
      .backgroundColor("#111")
      .linkDirectionalParticles(2)
      .linkDirectionalParticleSpeed(0.003)
      .linkOpacity(0.2)

      // Node üzerine gelindiğinde hover bilgisi
      .onNodeHover(node => {
        if (node) {
          document.getElementById('hover-info').innerText = `Node: ${node.label}`;
        } else {
          document.getElementById('hover-info').innerText = 'Hover üzerinde bir node için bilgi göreceksiniz.';
        }
      })
      
      // Node tıklanında içerik bilgisi gösterme
      .onNodeClick(node => {
        if (node && node.messages) {
          const messageContent = node.messages.map((msg, index) => 
            `${msg.role === "user" ? "User" : "ChatGPT"}: ${msg.content}`).join("\n\n");

          document.getElementById('node-info').innerText = 
            `Node: ${node.label}\n\nMesajlar:\n${messageContent}`;
        }
      });
  }

  Graph.graphData({ nodes, links });
}

// JSON verisini oku
fetch('parsed_conversations.json')
  .then(res => res.json())
  .then(data => {
    allData = data;

    // Dropdown doldur
    const uniqueMonths = new Set(
      data.map(d => `${d.year}-${String(d.month).padStart(2, '0')}`)
    );
    const select = document.getElementById('monthSelect');
    [...uniqueMonths].sort().forEach(m => {
      const opt = document.createElement('option');
      opt.value = m;
      opt.innerText = m;
      select.appendChild(opt);
    });

    // Varsayılan seçim yapıldığında çiz
    select.addEventListener('change', () => {
      const selected = select.value;
      if (selected) {
        const [y, m] = selected.split('-');
        const filtered = allData.filter(d => d.year == y && String(d.month).padStart(2, '0') == m);
        initGraph(filtered);
      }
    });
  });
