# Secure Demo Hosting Options

## ⚠️ Important Privacy Considerations

PTCC is designed as a **local-first, privacy-preserving system**. Any cloud hosting contradicts core value propositions. These options are **only for demonstration purposes** with synthetic data.

## Option 1: School Network Deployment (Recommended)

### Setup
```bash
# On school server or dedicated machine
git clone [ptcc-repo]
cd ptcc_standalone
./start-ptcc-fast.sh
```

### Access
- Internal URLs: `http://[school-server-ip]:8501` and `http://[school-server-ip]:5174`
- VPN access for remote stakeholders
- All data stays within school network

### Benefits
- Maintains privacy model
- Shows real deployment scenario
- IT can evaluate security
- Stakeholders see actual performance

## Option 2: Temporary Secure Hosting (Demo Only)

### Railway.app or DigitalOcean (with precautions)
```yaml
# railway.toml or docker-compose.yml
services:
  ptcc-demo:
    build: .
    environment:
      - DEMO_MODE=true
      - NO_REAL_DATA=true
    ports:
      - "8501:8501"
      - "5174:5174"
```

### Security Measures
- Environment variables to disable real data uploads
- Demo mode with read-only synthetic data
- Automatic data purging after 24 hours
- Password protection for demo access
- Clear "DEMO ONLY" warnings throughout interface

## Option 3: Docker Container for Portability

### Create Portable Demo
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
RUN cd frontend/mobile-pwa && npm install
RUN cd frontend/desktop-web && pip install -r requirements.txt

# Load demo data
RUN python -m backend.scripts.import_sample

EXPOSE 8001 8501 5174

CMD ["./start-ptcc-fast.sh"]
```

### Usage
```bash
# Build once
docker build -t ptcc-demo .

# Run anywhere
docker run -p 8501:8501 -p 5174:5174 -p 8001:8001 ptcc-demo
```

### Benefits
- Runs identically on any machine
- No dependency issues
- Self-contained demo
- Easy to distribute to IT teams

## Option 4: Screen Recording Demo

### Create Video Walkthrough
1. **Record 15-minute demo** following DEMO_SETUP.md script
2. **Host on private YouTube/Vimeo** with password protection
3. **Include live Q&A session** for follow-up questions
4. **Provide downloadable demo** for hands-on testing

### Benefits
- No security risks
- Available 24/7 for stakeholder review
- Can be shared with multiple decision-makers
- Shows real-time performance

## Option 5: Remote Screen Share (Zero Risk)

### Setup
1. **Schedule demo session** with stakeholders
2. **Run system locally** on your laptop
3. **Screen share via Teams/Zoom** for live demonstration
4. **Interactive Q&A** with real-time exploration

### Benefits
- Zero security risk - nothing leaves your machine
- Interactive demonstration
- Immediate answers to questions
- Shows actual system performance

## ❌ What NOT to Do

### Never Host on Public Cloud with:
- Real student data (even anonymized)
- Production database credentials
- Real school IP addresses or network details
- Actual teacher login information
- Live document upload capabilities

### Avoid Platforms Like:
- **Vercel/Netlify**: Frontend-only, no backend support
- **Heroku free tier**: Sleeps, looks unprofessional
- **AWS/GCP without expertise**: Security configuration risks
- **Any platform without HTTPS**: Data transmission risks

## Recommended Approach

### For Internal Stakeholders
**School Network Deployment** → Shows real deployment scenario

### For External Stakeholders  
**Docker Container** → Portable, consistent, secure

### For Asynchronous Review
**Screen Recording + Live Q&A** → Zero risk, high impact

### For Quick Demonstrations
**Local Laptop + Screen Share** → Maximum control, minimum risk

## Security Checklist for Any Demo

- [ ] Only synthetic student data
- [ ] No real school network details exposed
- [ ] Demo mode clearly labeled throughout interface
- [ ] No document upload capabilities in hosted version
- [ ] Password protection for remote access
- [ ] Automatic data purging after demo period
- [ ] Clear disclaimers about demo limitations
- [ ] Plan to destroy/reset after demonstration period

## Key Message for Stakeholders

**"This demo uses completely synthetic data to show system capabilities. In production, all data would remain on your school network with no cloud dependencies. The privacy-first architecture is a core feature, not a limitation."**

The demo should **reinforce** the privacy benefits, not compromise them.