-- Esquema para quality_control
CREATE TABLE quality_control (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    analysis_id TEXT NOT NULL UNIQUE,
    batch_id TEXT NOT NULL,
    product_type TEXT NOT NULL,
    operator_id TEXT NOT NULL,
    quality_score DECIMAL(4,1) NOT NULL,
    quality_grade TEXT NOT NULL,
    size_category TEXT NOT NULL,
    defects JSONB NOT NULL,
    batch_analysis JSONB NOT NULL,
    alerts JSONB,
    executive_summary JSONB NOT NULL,
    analyzed_at TIMESTAMPTZ DEFAULT NOW(),
    batch_completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para optimización
CREATE INDEX idx_quality_batch ON quality_control(batch_id);
CREATE INDEX idx_quality_product ON quality_control(product_type);
CREATE INDEX idx_quality_date ON quality_control(analyzed_at);
CREATE INDEX idx_quality_grade ON quality_control(quality_grade);
CREATE INDEX idx_quality_score ON quality_control(quality_score);

-- Vista para analytics de calidad
CREATE VIEW quality_analytics AS
SELECT 
    DATE(analyzed_at) as analysis_date,
    COUNT(*) as total_analyses,
    AVG(quality_score) as avg_quality_score,
    COUNT(*) FILTER (WHERE quality_grade = 'Premium') as premium_count,
    COUNT(*) FILTER (WHERE quality_grade = 'Rechazado') as rejected_count,
    MODE() WITHIN GROUP (ORDER BY product_type) as most_common_product,
    AVG((batch_analysis->>'rejection_rate')::DECIMAL) as avg_rejection_rate
FROM quality_control
GROUP BY DATE(analyzed_at);

-- Tabla para estándares de calidad
CREATE TABLE quality_standards (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    product_type TEXT NOT NULL UNIQUE,
    size_categories TEXT[] NOT NULL,
    size_thresholds DECIMAL[] NOT NULL,
    defect_categories TEXT[] NOT NULL,
    max_defects_per_unit INTEGER NOT NULL,
    min_quality_score DECIMAL(4,1) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla para configuración de alertas
CREATE TABLE alert_configuration (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    alert_type TEXT NOT NULL,
    threshold_value DECIMAL NOT NULL,
    severity TEXT NOT NULL,
    notification_channels TEXT[] NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
