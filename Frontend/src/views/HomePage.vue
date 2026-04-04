<template>
  <div class="home">
    <!-- Hero -->
    <section class="hero">
      <div class="hero-overlay"></div>
      <div class="hero-content">
        <h1>Plateforme de prescription<br />médicale sécurisée</h1>
        <p>Solution numérique pour les professionnels de santé et les pharmacies.</p>
      </div>
    </section>

    <!-- Access cards -->
    <section class="access-section">
      <h2>Accès professionnel</h2>
      <p class="subtitle">Sélectionnez votre profil pour vous connecter</p>

      <div class="cards-grid">
        <div class="access-card doctor-card">
          <div class="card-icon">&#128105;&#8205;&#9877;&#65039;</div>
          <h3>Espace Médecin</h3>
          <p>Créez et signez des ordonnances électroniques sécurisées pour vos patients.</p>
          <div class="card-actions">
            <router-link to="/login/doctor" class="btn btn-primary">Connexion</router-link>
            <router-link to="/signup/doctor" class="btn btn-outline">Inscription</router-link>
          </div>
        </div>

        <div class="access-card pharmacist-card">
          <div class="card-icon">&#128138;</div>
          <h3>Espace Pharmacien</h3>
          <p>Validez et gérez les ordonnances de vos clients en toute sécurité.</p>
          <div class="card-actions">
            <router-link to="/login/pharmacist" class="btn btn-success">Connexion</router-link>
            <router-link to="/signup/pharmacist" class="btn btn-outline">Inscription</router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section class="features-section">
      <h2>Une solution complète</h2>
      <div class="features-grid">
        <div class="feature">
          <div class="feature-icon">&#128274;</div>
          <h4>Sécurité maximale</h4>
          <p>Chiffrement des données et signatures électroniques pour une protection optimale.</p>
        </div>
        <div class="feature">
          <div class="feature-icon">&#9889;</div>
          <h4>Rapidité</h4>
          <p>Gagnez du temps avec une gestion simplifiée des ordonnances.</p>
        </div>
        <div class="feature">
          <div class="feature-icon">&#128241;</div>
          <h4>Accessibilité</h4>
          <p>Accédez à la plateforme depuis n'importe quel appareil, à tout moment.</p>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <div class="footer-content">
        <div>
          <h4>OrdoSafe</h4>
          <p>Solution innovante de gestion des ordonnances médicales.</p>
        </div>
        <div>
          <h4>Contact</h4>
          <p>contact@ordosafe.com</p>
          <p>+221 33 123 45 67</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.home {
  background: #fff;
}

/* Hero */
.hero {
  position: relative;
  background: linear-gradient(135deg, #1a1a2e, #16213e);
  padding: 6rem 2rem;
  text-align: center;
  color: #fff;
  overflow: hidden;
}
.hero-overlay {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 20% 80%, rgba(78, 115, 223, 0.2) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
}
.hero-content {
  position: relative;
  max-width: 700px;
  margin: 0 auto;
}
.hero h1 {
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 1rem;
  line-height: 1.2;
}
.hero p {
  font-size: 1.15rem;
  opacity: 0.85;
}

/* Access */
.access-section {
  padding: 4rem 2rem;
  text-align: center;
  max-width: 1000px;
  margin: 0 auto;
}
.access-section h2 {
  font-size: 1.8rem;
  font-weight: 700;
  color: #1a1a2e;
}
.subtitle {
  color: #666;
  margin-bottom: 2.5rem;
}
.cards-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}
@media (max-width: 768px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }
}
.access-card {
  background: #fff;
  border-radius: 16px;
  padding: 2.5rem 2rem;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s, box-shadow 0.3s;
}
.access-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
}
.doctor-card {
  border-bottom: 4px solid #4e73df;
}
.pharmacist-card {
  border-bottom: 4px solid #1cc88a;
}
.card-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}
.access-card h3 {
  font-size: 1.3rem;
  margin-bottom: 0.75rem;
  color: #1a1a2e;
}
.access-card p {
  color: #666;
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
}
.card-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
}

/* Buttons */
.btn {
  padding: 0.7rem 1.5rem;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.95rem;
  text-decoration: none;
  transition: all 0.2s;
  cursor: pointer;
  border: 2px solid transparent;
}
.btn-primary {
  background: #4e73df;
  color: #fff;
}
.btn-primary:hover {
  background: #3a5bc7;
}
.btn-success {
  background: #1cc88a;
  color: #fff;
}
.btn-success:hover {
  background: #17a673;
}
.btn-outline {
  background: transparent;
  color: #4e73df;
  border-color: #4e73df;
}
.btn-outline:hover {
  background: #4e73df;
  color: #fff;
}

/* Features */
.features-section {
  background: #f8f9fc;
  padding: 4rem 2rem;
  text-align: center;
}
.features-section h2 {
  font-size: 1.8rem;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 2.5rem;
}
.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
  max-width: 1000px;
  margin: 0 auto;
}
@media (max-width: 768px) {
  .features-grid {
    grid-template-columns: 1fr;
  }
}
.feature {
  background: #fff;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
}
.feature-icon {
  font-size: 2.5rem;
  margin-bottom: 0.75rem;
}
.feature h4 {
  color: #1a1a2e;
  margin-bottom: 0.5rem;
}
.feature p {
  color: #666;
  font-size: 0.9rem;
}

/* Footer */
.footer {
  background: #1a1a2e;
  color: #ccc;
  padding: 3rem 2rem;
}
.footer-content {
  max-width: 1000px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  gap: 2rem;
}
.footer h4 {
  color: #fff;
  margin-bottom: 0.5rem;
}
.footer p {
  font-size: 0.9rem;
  margin: 0.25rem 0;
}
</style>
