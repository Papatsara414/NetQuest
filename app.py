from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import json
import random
import os

app = Flask(__name__)
app.secret_key = 'netquest_secret_2024'
CORS(app)

# ========== ข้อมูลคำถามทั้งหมด ==========
QUESTIONS_DB = {
    "osi_model": [
        {
            "id": 1,
            "question": "OSI Model มีกี่ Layer?",
            "options": ["5 Layer", "6 Layer", "7 Layer", "8 Layer"],
            "answer": 2,
            "explanation": "OSI Model มีทั้งหมด 7 Layer ได้แก่ Physical, Data Link, Network, Transport, Session, Presentation, Application",
            "points": 10
        },
        {
            "id": 2,
            "question": "Layer ใดของ OSI Model รับผิดชอบการส่งข้อมูลเป็น Bits?",
            "options": ["Data Link", "Network", "Physical", "Transport"],
            "answer": 2,
            "explanation": "Physical Layer (Layer 1) รับผิดชอบการส่งข้อมูลเป็น bits ผ่านสื่อกลาง เช่น สาย UTP, Fiber Optic",
            "points": 10
        },
        {
            "id": 3,
            "question": "โปรโตคอล HTTP ทำงานอยู่ใน Layer ใด?",
            "options": ["Transport", "Session", "Presentation", "Application"],
            "answer": 3,
            "explanation": "HTTP ทำงานใน Application Layer (Layer 7) ซึ่งเป็น Layer ที่ใกล้ชิดกับผู้ใช้มากที่สุด",
            "points": 15
        },
        {
            "id": 4,
            "question": "MAC Address ทำงานใน Layer ใด?",
            "options": ["Physical", "Data Link", "Network", "Transport"],
            "answer": 1,
            "explanation": "MAC Address ใช้ใน Data Link Layer (Layer 2) สำหรับระบุตัวตนของ Network Interface Card",
            "points": 15
        },
        {
            "id": 5,
            "question": "IP Address ทำงานใน Layer ใดของ OSI?",
            "options": ["Data Link", "Network", "Transport", "Session"],
            "answer": 1,
            "explanation": "IP Address ทำงานใน Network Layer (Layer 3) รับผิดชอบการ Routing ข้อมูลระหว่าง Network",
            "points": 10
        }
    ],
    "tcp_ip": [
        {
            "id": 6,
            "question": "TCP ย่อมาจากอะไร?",
            "options": [
                "Transfer Control Protocol",
                "Transmission Control Protocol",
                "Transport Communication Protocol",
                "Total Control Packet"
            ],
            "answer": 1,
            "explanation": "TCP ย่อมาจาก Transmission Control Protocol เป็นโปรโตคอลที่เชื่อถือได้ มีการยืนยันการส่งข้อมูล",
            "points": 10
        },
        {
            "id": 7,
            "question": "TCP Three-Way Handshake คืออะไร?",
            "options": [
                "SYN → ACK → FIN",
                "SYN → SYN-ACK → ACK",
                "ACK → SYN → FIN",
                "SYN → FIN → ACK"
            ],
            "answer": 1,
            "explanation": "TCP Three-Way Handshake คือ SYN → SYN-ACK → ACK เพื่อสร้าง Connection ก่อนส่งข้อมูล",
            "points": 20
        },
        {
            "id": 8,
            "question": "UDP แตกต่างจาก TCP อย่างไร?",
            "options": [
                "UDP เร็วกว่าแต่ไม่มีการยืนยันการส่ง",
                "UDP ช้ากว่าแต่เชื่อถือได้กว่า",
                "UDP ใช้สำหรับ File Transfer เท่านั้น",
                "UDP ต้องมี Connection ก่อนส่งข้อมูล"
            ],
            "answer": 0,
            "explanation": "UDP (User Datagram Protocol) ส่งข้อมูลได้เร็วกว่าแต่ไม่มีการยืนยันการส่ง เหมาะสำหรับ Streaming, Gaming",
            "points": 15
        },
        {
            "id": 9,
            "question": "Port 80 ใช้สำหรับโปรโตคอลใด?",
            "options": ["HTTPS", "FTP", "HTTP", "SSH"],
            "answer": 2,
            "explanation": "Port 80 เป็น Default Port ของ HTTP (HyperText Transfer Protocol) สำหรับเว็บทั่วไป",
            "points": 10
        },
        {
            "id": 10,
            "question": "Port 443 ใช้สำหรับโปรโตคอลใด?",
            "options": ["HTTP", "HTTPS", "FTP", "SMTP"],
            "answer": 1,
            "explanation": "Port 443 เป็น Default Port ของ HTTPS ซึ่งเป็น HTTP ที่เข้ารหัสด้วย SSL/TLS",
            "points": 10
        }
    ],
    "ip_addressing": [
        {
            "id": 11,
            "question": "IPv4 Address มีขนาดกี่ bits?",
            "options": ["16 bits", "32 bits", "64 bits", "128 bits"],
            "answer": 1,
            "explanation": "IPv4 Address มีขนาด 32 bits แบ่งเป็น 4 Octet แต่ละ Octet มี 8 bits",
            "points": 10
        },
        {
            "id": 12,
            "question": "Subnet Mask 255.255.255.0 มี CIDR notation เป็นอะไร?",
            "options": ["/16", "/24", "/32", "/8"],
            "answer": 1,
            "explanation": "255.255.255.0 = /24 เพราะมี 24 bits ที่เป็น 1 (255 = 11111111 × 3 = 24 bits)",
            "points": 20
        },
        {
            "id": 13,
            "question": "IP Address 192.168.1.1 อยู่ใน Class ใด?",
            "options": ["Class A", "Class B", "Class C", "Class D"],
            "answer": 2,
            "explanation": "192.168.x.x เป็น Private IP ใน Class C (192-223) ใช้สำหรับ LAN ภายในองค์กร",
            "points": 15
        },
        {
            "id": 14,
            "question": "Loopback Address คือ IP อะไร?",
            "options": ["0.0.0.0", "255.255.255.255", "127.0.0.1", "192.168.0.1"],
            "answer": 2,
            "explanation": "127.0.0.1 คือ Loopback Address ใช้ทดสอบ Network Stack ของตัวเองโดยไม่ต้องส่งออก Network",
            "points": 10
        },
        {
            "id": 15,
            "question": "IPv6 Address มีขนาดกี่ bits?",
            "options": ["32 bits", "64 bits", "128 bits", "256 bits"],
            "answer": 2,
            "explanation": "IPv6 Address มีขนาด 128 bits รองรับ Address ได้มากกว่า IPv4 อย่างมหาศาล",
            "points": 15
        }
    ],
    "network_devices": [
        {
            "id": 16,
            "question": "Router ทำหน้าที่อะไร?",
            "options": [
                "เชื่อมต่ออุปกรณ์ใน LAN เดียวกัน",
                "เชื่อมต่อระหว่าง Network ต่างๆ และ Route ข้อมูล",
                "แปลงสัญญาณ Analog เป็น Digital",
                "กรอง Traffic ด้วย MAC Address"
            ],
            "answer": 1,
            "explanation": "Router ทำหน้าที่เชื่อมต่อระหว่าง Network ต่างๆ และเลือกเส้นทาง (Route) ที่ดีที่สุดในการส่งข้อมูล",
            "points": 10
        },
        {
            "id": 17,
            "question": "Switch แตกต่างจาก Hub อย่างไร?",
            "options": [
                "Switch ส่งข้อมูลไปทุก Port, Hub ส่งเฉพาะ Port ปลายทาง",
                "Switch ส่งข้อมูลเฉพาะ Port ปลายทาง, Hub ส่งไปทุก Port",
                "Switch ทำงานใน Layer 3, Hub ทำงานใน Layer 2",
                "ไม่มีความแตกต่าง"
            ],
            "answer": 1,
            "explanation": "Switch ฉลาดกว่า Hub โดยส่งข้อมูลไปยัง Port ปลายทางเท่านั้น (ใช้ MAC Table) ทำให้ลด Collision",
            "points": 20
        },
        {
            "id": 18,
            "question": "Firewall ทำหน้าที่อะไร?",
            "options": [
                "เพิ่มความเร็ว Network",
                "กรอง Network Traffic ตาม Rules ที่กำหนด",
                "แจก IP Address ให้อุปกรณ์",
                "แปลง Domain Name เป็น IP"
            ],
            "answer": 1,
            "explanation": "Firewall ทำหน้าที่กรอง Traffic ที่เข้า-ออก Network ตาม Security Rules เพื่อป้องกัน Unauthorized Access",
            "points": 15
        },
        {
            "id": 19,
            "question": "DHCP Server ทำหน้าที่อะไร?",
            "options": [
                "แปลง Domain เป็น IP",
                "จัดการ Email",
                "แจก IP Address อัตโนมัติให้อุปกรณ์",
                "เข้ารหัสข้อมูล"
            ],
            "answer": 2,
            "explanation": "DHCP (Dynamic Host Configuration Protocol) Server แจก IP Address, Subnet Mask, Gateway, DNS ให้อุปกรณ์อัตโนมัติ",
            "points": 10
        },
        {
            "id": 20,
            "question": "DNS ย่อมาจากอะไร?",
            "options": [
                "Dynamic Network System",
                "Domain Name System",
                "Digital Network Service",
                "Data Name Server"
            ],
            "answer": 1,
            "explanation": "DNS ย่อมาจาก Domain Name System ทำหน้าที่แปลง Domain Name (เช่น google.com) เป็น IP Address",
            "points": 10
        }
    ],
    "security": [
        {
            "id": 21,
            "question": "SSL/TLS ใช้สำหรับอะไร?",
            "options": [
                "เพิ่มความเร็วในการส่งข้อมูล",
                "เข้ารหัสข้อมูลระหว่างการส่ง",
                "แจก IP Address",
                "Route ข้อมูลระหว่าง Network"
            ],
            "answer": 1,
            "explanation": "SSL/TLS (Secure Sockets Layer/Transport Layer Security) เข้ารหัสข้อมูลระหว่างส่ง ใช้ใน HTTPS",
            "points": 15
        },
        {
            "id": 22,
            "question": "VPN คืออะไร?",
            "options": [
                "Virtual Private Network - เชื่อมต่อ Network ปลอดภัยผ่าน Internet",
                "Very Public Network - Network สาธารณะ",
                "Virtual Protocol Node - จุดเชื่อมต่อ",
                "Verified Packet Network - Network ที่ตรวจสอบ Packet"
            ],
            "answer": 0,
            "explanation": "VPN (Virtual Private Network) สร้างอุโมงค์เข้ารหัส (Encrypted Tunnel) เพื่อส่งข้อมูลอย่างปลอดภัยผ่าน Internet",
            "points": 10
        },
        {
            "id": 23,
            "question": "DDoS Attack คืออะไร?",
            "options": [
                "การขโมยรหัสผ่าน",
                "การโจมตีด้วยการส่ง Traffic จำนวนมากเพื่อทำให้ Server ล่ม",
                "การดักฟัง Network Traffic",
                "การเข้าถึงข้อมูลโดยไม่ได้รับอนุญาต"
            ],
            "answer": 1,
            "explanation": "DDoS (Distributed Denial of Service) คือการโจมตีโดยส่ง Traffic จำนวนมากจากหลาย Source เพื่อทำให้ Server ล่ม",
            "points": 20
        },
        {
            "id": 24,
            "question": "WPA2 ใช้สำหรับอะไร?",
            "options": [
                "เข้ารหัส Wi-Fi Network",
                "เพิ่มความเร็ว Wi-Fi",
                "ขยายสัญญาณ Wi-Fi",
                "แจก IP ใน Wi-Fi"
            ],
            "answer": 0,
            "explanation": "WPA2 (Wi-Fi Protected Access 2) ใช้เข้ารหัสการเชื่อมต่อ Wireless Network ด้วย AES Encryption",
            "points": 15
        },
        {
            "id": 25,
            "question": "Man-in-the-Middle Attack คืออะไร?",
            "options": [
                "การโจมตีโดยการแทรกตัวระหว่างการสื่อสาร 2 ฝ่าย",
                "การโจมตีทางกายภาพ",
                "การส่ง Email หลอกลวง",
                "การเดา Password"
            ],
            "answer": 0,
            "explanation": "Man-in-the-Middle Attack คือผู้โจมตีแทรกตัวระหว่างการสื่อสาร ดักฟังหรือแก้ไขข้อมูลโดยที่ทั้งสองฝ่ายไม่รู้",
            "points": 20
        }
    ]
}

LESSONS = {
    "osi_model": {
        "title": "OSI Model",
        "icon": "🏗️",
        "description": "เรียนรู้โครงสร้างของ OSI 7 Layer",
        "color": "#FF6B35",
        "xp": 50,
        "content": """
        <h3>OSI Model คืออะไร?</h3>
        <p>OSI (Open Systems Interconnection) Model คือมาตรฐานสากลที่อธิบายวิธีการสื่อสารของระบบเครือข่าย แบ่งออกเป็น 7 Layer</p>
        
        <div class="layer-grid">
            <div class="layer-item" data-layer="7">
                <span class="layer-num">7</span>
                <span class="layer-name">Application</span>
                <span class="layer-desc">HTTP, FTP, SMTP, DNS</span>
            </div>
            <div class="layer-item" data-layer="6">
                <span class="layer-num">6</span>
                <span class="layer-name">Presentation</span>
                <span class="layer-desc">SSL/TLS, Encryption</span>
            </div>
            <div class="layer-item" data-layer="5">
                <span class="layer-num">5</span>
                <span class="layer-name">Session</span>
                <span class="layer-desc">NetBIOS, RPC</span>
            </div>
            <div class="layer-item" data-layer="4">
                <span class="layer-num">4</span>
                <span class="layer-name">Transport</span>
                <span class="layer-desc">TCP, UDP</span>
            </div>
            <div class="layer-item" data-layer="3">
                <span class="layer-num">3</span>
                <span class="layer-name">Network</span>
                <span class="layer-desc">IP, Router</span>
            </div>
            <div class="layer-item" data-layer="2">
                <span class="layer-num">2</span>
                <span class="layer-name">Data Link</span>
                <span class="layer-desc">MAC, Switch</span>
            </div>
            <div class="layer-item" data-layer="1">
                <span class="layer-num">1</span>
                <span class="layer-name">Physical</span>
                <span class="layer-desc">Cables, Hubs</span>
            </div>
        </div>
        
        <div class="memory-tip">
            💡 <strong>จำง่ายๆ:</strong> "All People Seem To Need Data Processing"
        </div>
        """
    },
    "tcp_ip": {
        "title": "TCP/IP Protocol",
        "icon": "🔌",
        "description": "เข้าใจการทำงานของ TCP และ UDP",
        "color": "#4ECDC4",
        "xp": 60,
        "content": """
        <h3>TCP vs UDP</h3>
        <div class="comparison-table">
            <div class="compare-col tcp">
                <h4>TCP 🛡️</h4>
                <ul>
                    <li>✅ เชื่อถือได้</li>
                    <li>✅ มีการยืนยัน</li>
                    <li>✅ เรียงลำดับข้อมูล</li>
                    <li>❌ ช้ากว่า UDP</li>
                    <li>📦 Web, Email, FTP</li>
                </ul>
            </div>
            <div class="compare-col udp">
                <h4>UDP ⚡</h4>
                <ul>
                    <li>❌ ไม่มีการยืนยัน</li>
                    <li>❌ อาจสูญหาย</li>
                    <li>✅ เร็วมาก</li>
                    <li>✅ Overhead น้อย</li>
                    <li>🎮 Gaming, Video Call</li>
                </ul>
            </div>
        </div>
        
        <h3>Well-Known Ports</h3>
        <div class="port-grid">
            <div class="port-item">Port 21 = FTP</div>
            <div class="port-item">Port 22 = SSH</div>
            <div class="port-item">Port 25 = SMTP</div>
            <div class="port-item">Port 53 = DNS</div>
            <div class="port-item">Port 80 = HTTP</div>
            <div class="port-item">Port 443 = HTTPS</div>
        </div>
        """
    },
    "ip_addressing": {
        "title": "IP Addressing",
        "icon": "📍",
        "description": "IPv4, IPv6 และ Subnetting",
        "color": "#A855F7",
        "xp": 70,
        "content": """
        <h3>IPv4 Address</h3>
        <p>IPv4 มีขนาด 32 bits เขียนเป็น 4 Octet คั่นด้วยจุด เช่น 192.168.1.100</p>
        
        <div class="ip-visual">
            <div class="octet">192</div>
            <div class="dot">.</div>
            <div class="octet">168</div>
            <div class="dot">.</div>
            <div class="octet">1</div>
            <div class="dot">.</div>
            <div class="octet">100</div>
        </div>
        
        <h3>Private IP Ranges</h3>
        <div class="ip-table">
            <div class="ip-row header">
                <span>Class</span><span>Range</span><span>ใช้งาน</span>
            </div>
            <div class="ip-row">
                <span>A</span><span>10.0.0.0/8</span><span>องค์กรใหญ่</span>
            </div>
            <div class="ip-row">
                <span>B</span><span>172.16-31.0.0/12</span><span>องค์กรกลาง</span>
            </div>
            <div class="ip-row">
                <span>C</span><span>192.168.0.0/16</span><span>บ้าน/ออฟฟิศ</span>
            </div>
        </div>
        """
    },
    "network_devices": {
        "title": "Network Devices",
        "icon": "🖥️",
        "description": "Router, Switch, Firewall และอื่นๆ",
        "color": "#F59E0B",
        "xp": 55,
        "content": """
        <h3>อุปกรณ์เครือข่ายหลัก</h3>
        
        <div class="device-grid">
            <div class="device-card">
                <div class="device-icon">🌐</div>
                <h4>Router</h4>
                <p>เชื่อมต่อ Network ต่างๆ เลือก Route ที่ดีที่สุด ทำงานใน Layer 3</p>
            </div>
            <div class="device-card">
                <div class="device-icon">🔀</div>
                <h4>Switch</h4>
                <p>เชื่อมอุปกรณ์ใน LAN ส่งข้อมูลเฉพาะ Port ปลายทาง ทำงานใน Layer 2</p>
            </div>
            <div class="device-card">
                <div class="device-icon">🛡️</div>
                <h4>Firewall</h4>
                <p>กรอง Traffic ตาม Rules ป้องกัน Unauthorized Access</p>
            </div>
            <div class="device-card">
                <div class="device-icon">📡</div>
                <h4>Access Point</h4>
                <p>กระจายสัญญาณ Wi-Fi ให้อุปกรณ์ Wireless เชื่อมต่อได้</p>
            </div>
        </div>
        """
    },
    "security": {
        "title": "Network Security",
        "icon": "🔒",
        "description": "การรักษาความปลอดภัย Network",
        "color": "#EF4444",
        "xp": 80,
        "content": """
        <h3>ภัยคุกคามทางเครือข่าย</h3>
        
        <div class="threat-list">
            <div class="threat-item">
                <span class="threat-icon">💀</span>
                <div>
                    <strong>DDoS Attack</strong>
                    <p>ส่ง Traffic จำนวนมากเพื่อทำให้ Server ล่ม</p>
                </div>
            </div>
            <div class="threat-item">
                <span class="threat-icon">🕵️</span>
                <div>
                    <strong>Man-in-the-Middle</strong>
                    <p>แทรกตัวระหว่างการสื่อสารเพื่อดักข้อมูล</p>
                </div>
            </div>
            <div class="threat-item">
                <span class="threat-icon">🎣</span>
                <div>
                    <strong>Phishing</strong>
                    <p>หลอกให้เปิดเผยข้อมูลสำคัญผ่าน Email/Website ปลอม</p>
                </div>
            </div>
        </div>
        
        <h3>การป้องกัน</h3>
        <div class="protection-grid">
            <div class="protect-item">🔒 ใช้ HTTPS ทุกครั้ง</div>
            <div class="protect-item">🔑 เปิด 2FA</div>
            <div class="protect-item">🛡️ ติดตั้ง Firewall</div>
            <div class="protect-item">📱 อัพเดท Software</div>
            <div class="protect-item">🌐 ใช้ VPN</div>
            <div class="protect-item">💾 Backup ข้อมูล</div>
        </div>
        """
    }
}

# ========== Routes ==========

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/lessons', methods=['GET'])
def get_lessons():
    lessons_list = []
    for key, lesson in LESSONS.items():
        lessons_list.append({
            "id": key,
            "title": lesson["title"],
            "icon": lesson["icon"],
            "description": lesson["description"],
            "color": lesson["color"],
            "xp": lesson["xp"],
            "question_count": len(QUESTIONS_DB.get(key, []))
        })
    return jsonify(lessons_list)

@app.route('/api/lesson/<lesson_id>', methods=['GET'])
def get_lesson(lesson_id):
    if lesson_id not in LESSONS:
        return jsonify({"error": "Lesson not found"}), 404
    lesson = LESSONS[lesson_id].copy()
    lesson["id"] = lesson_id
    return jsonify(lesson)

@app.route('/api/questions/<lesson_id>', methods=['GET'])
def get_questions(lesson_id):
    if lesson_id not in QUESTIONS_DB:
        return jsonify({"error": "Questions not found"}), 404
    questions = QUESTIONS_DB[lesson_id].copy()
    random.shuffle(questions)
    # ซ่อน answer จาก client
    for q in questions:
        q['has_answer'] = True
    return jsonify(questions)

@app.route('/api/check-answer', methods=['POST'])
def check_answer():
    data = request.json
    lesson_id = data.get('lesson_id')
    question_id = data.get('question_id')
    selected = data.get('selected')
    
    if lesson_id not in QUESTIONS_DB:
        return jsonify({"error": "Invalid lesson"}), 400
    
    questions = QUESTIONS_DB[lesson_id]
    question = next((q for q in questions if q['id'] == question_id), None)
    
    if not question:
        return jsonify({"error": "Question not found"}), 404
    
    is_correct = selected == question['answer']
    
    return jsonify({
        "correct": is_correct,
        "correct_answer": question['answer'],
        "explanation": question['explanation'],
        "points": question['points'] if is_correct else 0
    })

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    # Mock leaderboard data
    leaderboard = [
        {"rank": 1, "name": "NetworkNinja", "xp": 2450, "streak": 15, "avatar": "🥷"},
        {"rank": 2, "name": "TCPMaster", "xp": 2100, "streak": 8, "avatar": "🎮"},
        {"rank": 3, "name": "RouterKing", "xp": 1890, "streak": 12, "avatar": "👑"},
        {"rank": 4, "name": "PacketHero", "xp": 1650, "streak": 5, "avatar": "🦸"},
        {"rank": 5, "name": "SubnetPro", "xp": 1420, "streak": 7, "avatar": "⚡"},
    ]
    return jsonify(leaderboard)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)