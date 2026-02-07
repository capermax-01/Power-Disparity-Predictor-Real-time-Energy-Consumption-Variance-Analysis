
"""
GAN-based Synthetic Energy Data Generator
Generates 20x synthetic data from real energy dataset with >90% quality validation
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from scipy import stats
import warnings
from config import BASE_DIR

warnings.filterwarnings('ignore')

# Set seeds for reproducibility
np.random.seed(42)
tf.random.set_seed(42)

class EnergyGAN:
    def __init__(self, data_path, latent_dim=100):
        self.data_path = data_path
        self.latent_dim = latent_dim
        self.scalers = {}
        self.label_encoders = {}
        self.column_info = {}
        self.X_scaled = None
        self.real_data = None
        
    def load_and_prepare_data(self):
        """Load CSV and prepare data for GAN training"""
        print("Loading real dataset...")
        self.real_data = pd.read_csv(self.data_path)
        print(f"Dataset shape: {self.real_data.shape}")
        print(f"Columns: {list(self.real_data.columns)}")
        
        # Separate numeric and categorical columns
        numeric_cols = self.real_data.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = self.real_data.select_dtypes(include=['object']).columns.tolist()
        
        # Remove timestamp for processing
        categorical_cols = [col for col in categorical_cols if col != 'timestamp']
        
        print(f"\nNumeric columns ({len(numeric_cols)}): {numeric_cols}")
        print(f"Categorical columns ({len(categorical_cols)}): {categorical_cols}")
        
        # Store column info
        self.column_info = {
            'numeric': numeric_cols,
            'categorical': categorical_cols,
            'all': numeric_cols + categorical_cols
        }
        
        return numeric_cols, categorical_cols
    
    def encode_categorical_features(self, df, fit=False):
        """Encode categorical variables"""
        df_copy = df.copy()
        
        for col in self.column_info['categorical']:
            if fit:
                self.label_encoders[col] = LabelEncoder()
                df_copy[col] = self.label_encoders[col].fit_transform(df_copy[col].astype(str))
            else:
                df_copy[col] = self.label_encoders[col].transform(df_copy[col].astype(str))
        
        return df_copy
    
    def preprocess_data(self):
        """Preprocess data for GAN"""
        # Encode categorical features
        df_encoded = self.encode_categorical_features(self.real_data, fit=True)
        df_encoded = df_encoded.drop('timestamp', axis=1)
        
        # Scale numeric features
        scaler = StandardScaler()
        self.X_scaled = scaler.fit_transform(df_encoded[self.column_info['numeric']])
        self.scalers['numeric'] = scaler
        
        # Scale categorical features (already encoded, scale to [0,1])
        scaler_cat = StandardScaler()
        categorical_encoded = df_encoded[self.column_info['categorical']].values
        categorical_scaled = scaler_cat.fit_transform(categorical_encoded)
        self.scalers['categorical'] = scaler_cat
        
        # Combine scaled features
        X_train = np.concatenate([self.X_scaled, categorical_scaled], axis=1)
        
        print(f"Preprocessed data shape: {X_train.shape}")
        return X_train
    
    def build_generator(self, input_dim):
        """Build generator network"""
        model = keras.Sequential([
            layers.Dense(256, activation='relu', input_dim=input_dim),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            layers.Dense(512, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            layers.Dense(1024, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            layers.Dense(input_dim, activation='tanh')
        ])
        
        return model
    
    def build_discriminator(self, input_dim):
        """Build discriminator network"""
        model = keras.Sequential([
            layers.Dense(512, activation='relu', input_dim=input_dim),
            layers.Dropout(0.3),
            
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.3),
            
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.3),
            
            layers.Dense(1, activation='sigmoid')
        ])
        
        return model
    
    def train_gan(self, X_train, epochs=300, batch_size=64):
        """Train the GAN"""
        print(f"\nTraining GAN for {epochs} epochs...")
        
        input_dim = X_train.shape[1]
        
        # Build generator and discriminator
        generator = self.build_generator(self.latent_dim)
        discriminator = self.build_discriminator(input_dim)
        
        # Compile discriminator
        discriminator.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.0002, beta_1=0.5),
            loss='binary_crossentropy'
        )
        
        # Build combined model
        discriminator.trainable = False
        gan_input = keras.Input(shape=(self.latent_dim,))
        gan_output = discriminator(generator(gan_input))
        gan = keras.Model(gan_input, gan_output)
        
        gan.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.0002, beta_1=0.5),
            loss='binary_crossentropy'
        )
        
        # Training loop
        d_losses = []
        g_losses = []
        
        for epoch in range(epochs):
            # Get random batch of real data
            idx = np.random.randint(0, X_train.shape[0], batch_size)
            real_data = X_train[idx]
            
            # Generate fake data
            noise = np.random.normal(0, 1, (batch_size, self.latent_dim))
            fake_data = generator.predict(noise, verbose=0)
            
            # Train discriminator
            X_combined = np.concatenate([real_data, fake_data])
            y_combined = np.concatenate([np.ones((batch_size, 1)), np.zeros((batch_size, 1))])
            
            d_loss = discriminator.train_on_batch(X_combined, y_combined)
            d_losses.append(d_loss)
            
            # Train generator
            noise = np.random.normal(0, 1, (batch_size, self.latent_dim))
            y_generator = np.ones((batch_size, 1))
            g_loss = gan.train_on_batch(noise, y_generator)
            g_losses.append(g_loss)
            
            if (epoch + 1) % 50 == 0:
                print(f"Epoch {epoch + 1}/{epochs} - D Loss: {d_loss:.4f}, G Loss: {g_loss:.4f}")
        
        print("Training completed!")
        self.generator = generator
        self.discriminator = discriminator
        
        return generator
    
    def generate_synthetic_data(self, num_samples):
        """Generate synthetic data"""
        print(f"\nGenerating {num_samples} synthetic samples...")
        noise = np.random.normal(0, 1, (num_samples, self.latent_dim))
        synthetic_scaled = self.generator.predict(noise, verbose=0)
        
        # Clip to valid range
        synthetic_scaled = np.clip(synthetic_scaled, -3, 3)
        
        return synthetic_scaled
    
    def inverse_transform_data(self, synthetic_scaled):
        """Convert scaled synthetic data back to original scale"""
        # Split numeric and categorical
        num_features = len(self.column_info['numeric'])
        
        numeric_scaled = synthetic_scaled[:, :num_features]
        categorical_scaled = synthetic_scaled[:, num_features:]
        
        # Inverse transform numeric features
        numeric_data = self.scalers['numeric'].inverse_transform(numeric_scaled)
        
        # Inverse transform categorical features
        categorical_data = self.scalers['categorical'].inverse_transform(categorical_scaled)
        categorical_data = np.round(categorical_data).astype(int)
        
        # Combine
        combined = np.concatenate([numeric_data, categorical_data], axis=1)
        
        # Create DataFrame
        synthetic_df = pd.DataFrame(
            combined,
            columns=self.column_info['all']
        )
        
        # Decode categorical features
        for col in self.column_info['categorical']:
            col_idx = self.column_info['all'].index(col)
            synthetic_df[col] = synthetic_df[col].astype(int)
            # Clip to valid range of label encoder classes
            max_val = len(self.label_encoders[col].classes_) - 1
            synthetic_df[col] = synthetic_df[col].clip(0, max_val)
            synthetic_df[col] = self.label_encoders[col].inverse_transform(
                synthetic_df[col].values
            )
        
        return synthetic_df
    
    def calculate_quality_metrics(self, real_df, synthetic_df):
        """Calculate quality metrics between real and synthetic data"""
        metrics = {}
        
        # Numeric features comparison
        numeric_cols = self.column_info['numeric']
        correlation_scores = []
        ks_scores = []
        
        for col in numeric_cols:
            real_vals = real_df[col].values
            synth_vals = synthetic_df[col].values
            
            # Mean comparison
            real_mean = np.mean(real_vals)
            synth_mean = np.mean(synth_vals)
            
            # KS test (0 = identical, 1 = different)
            ks_stat, _ = stats.ks_2samp(real_vals, synth_vals)
            ks_score = max(0, 1 - ks_stat)  # Convert to similarity score
            ks_scores.append(ks_score)
            
            # Correlation of statistical properties
            correlation_scores.append(ks_score)
        
        metrics['numeric_ks_similarity'] = np.mean(ks_scores) * 100
        
        # Categorical features comparison
        categorical_cols = self.column_info['categorical']
        category_scores = []
        
        for col in categorical_cols:
            real_dist = real_df[col].value_counts(normalize=True)
            synth_dist = synthetic_df[col].value_counts(normalize=True)
            
            # Calculate distribution similarity (Jensen-Shannon divergence)
            # Convert to probability distributions
            all_categories = set(real_dist.index) | set(synth_dist.index)
            real_probs = np.array([real_dist.get(cat, 0) for cat in all_categories])
            synth_probs = np.array([synth_dist.get(cat, 0) for cat in all_categories])
            
            # Normalize
            real_probs = real_probs / np.sum(real_probs)
            synth_probs = synth_probs / np.sum(synth_probs)
            
            # Jensen-Shannon divergence
            js_div = stats.entropy(real_probs, synth_probs)
            js_score = max(0, 1 - js_div / np.log(2))  # Convert to similarity
            category_scores.append(js_score)
        
        if category_scores:
            metrics['categorical_similarity'] = np.mean(category_scores) * 100
        
        # Overall quality score
        all_scores = ks_scores + category_scores
        overall_score = np.mean(all_scores) * 100
        metrics['overall_quality'] = overall_score
        
        return metrics
    
    def run_pipeline(self, num_synthetic_samples=None):
        """Run complete pipeline"""
        # Load and prepare
        numeric_cols, categorical_cols = self.load_and_prepare_data()
        
        # Preprocess
        X_train = self.preprocess_data()
        
        # Generate synthetic size (20x real data)
        if num_synthetic_samples is None:
            num_synthetic_samples = X_train.shape[0] * 20
        
        print(f"Real samples: {X_train.shape[0]}")
        print(f"Target synthetic samples: {num_synthetic_samples}")
        
        # Train GAN
        self.train_gan(X_train, epochs=300, batch_size=64)
        
        # Generate synthetic data
        synthetic_scaled = self.generate_synthetic_data(num_synthetic_samples)
        synthetic_df = self.inverse_transform_data(synthetic_scaled)
        
        # Add timestamp simulation
        real_timestamps = self.real_data['timestamp'].values
        synthetic_df.insert(0, 'timestamp', 
                           f"{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Calculate quality metrics
        print("\n" + "="*60)
        print("QUALITY VALIDATION METRICS")
        print("="*60)
        
        metrics = self.calculate_quality_metrics(
            self.real_data[self.column_info['numeric'] + self.column_info['categorical']],
            synthetic_df[self.column_info['numeric'] + self.column_info['categorical']]
        )
        
        print(f"Numeric Features KS Similarity: {metrics['numeric_ks_similarity']:.2f}%")
        if 'categorical_similarity' in metrics:
            print(f"Categorical Features Similarity: {metrics['categorical_similarity']:.2f}%")
        print(f"\n{'='*60}")
        print(f"OVERALL QUALITY SCORE: {metrics['overall_quality']:.2f}%")
        print(f"{'='*60}")
        
        # Check if accuracy > 90%
        if metrics['overall_quality'] >= 90:
            print("✓ Quality target ACHIEVED (>90%)")
        else:
            print(f"⚠ Quality: {metrics['overall_quality']:.2f}% - Below 90% target")
        
        # Save synthetic data
        output_path = self.data_path.replace('.csv', '_synthetic_20x.csv')
        synthetic_df.to_csv(output_path, index=False)
        print(f"\n✓ Synthetic data saved to: {output_path}")
        print(f"  Shape: {synthetic_df.shape}")
        
        return synthetic_df, metrics


def main():
    # Initialize GAN
    data_path = BASE_DIR / "energy_data.csv"
    
    if not data_path.exists():
        print(f"⚠ Energy data file not found: {data_path}")
        # Try a sample file if available
        sample_path = BASE_DIR / "appliances_consolidated.csv"
        if sample_path.exists():
            data_path = sample_path
            print(f"Using consolidated CSV as fallback: {data_path}")
        else:
            print("No suitable data file found for GAN demo.")
            return

    gan = EnergyGAN(str(data_path), latent_dim=100)
    
    # Run complete pipeline
    synthetic_data, metrics = gan.run_pipeline()
    
    print("\n" + "="*60)
    print("SYNTHETIC DATA SAMPLE (First 10 rows):")
    print("="*60)
    print(synthetic_data.head(10))
    
    print("\n" + "="*60)
    print("REAL vs SYNTHETIC - STATISTICS COMPARISON")
    print("="*60)
    
    # Statistics comparison for numeric columns
    numeric_cols = [col for col in gan.column_info['numeric']]
    print("\nNumeric Features Comparison:")
    for col in numeric_cols[:5]:  # Show first 5
        real_mean = gan.real_data[col].mean()
        real_std = gan.real_data[col].std()
        synth_mean = synthetic_data[col].mean()
        synth_std = synthetic_data[col].std()
        
        print(f"\n{col}:")
        print(f"  Real  - Mean: {real_mean:.4f}, Std: {real_std:.4f}")
        print(f"  Synth - Mean: {synth_mean:.4f}, Std: {synth_std:.4f}")


if __name__ == "__main__":
    main()
