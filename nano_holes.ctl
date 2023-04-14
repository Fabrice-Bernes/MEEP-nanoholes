(set! resolution 45)


(define HoleQty 5)
(define HoleSep 1)
(define HoleWid 0.8)
(define HoleDpt 0.3)
(define TotalLen ( - (* (+ HoleQty 1) HoleSep) HoleWid))

(define GlassDpt 2)

(define SrcDist 2.8)
(define SrcTheta 30) ; Angle is given in degrees to be converted to radian
(set! SrcTheta (* (/ pi 180) SrcTheta))


(set! geometry-lattice (make lattice (size (+ TotalLen 1) 8 no-size)))  ; Sim space


(set! geometry (list
    (make block
    (material BK7)
    (size infinity GlassDpt infinity )
    (center 0 (* -1 (/ (+ HoleDpt GlassDpt) 2))))
    ))

(set! geometry(
    append geometry (
    map ( lambda (n) (
    make block
    (material Au)
    (size (- HoleSep HoleWid) HoleDpt infinity)
    (center  (- (* n HoleSep) (/ TotalLen 2)) 0))) 
    (arith-sequence 0 1 (+ HoleQty 1))
        )
    )
)


(set! pml-layers (list (make pml (thickness 1.0))))


(set! sources (list
               (make source
                 (src (make continuous-src (frequency 0.15)))
                 (component Ez)
                 (center 0 (* -1 SrcDist)))
               (make source
                 (src (make continuous-src (frequency 0.85)))
                 (component Ez)
                 (center (* SrcDist (sin SrcTheta)) (* -1 (* SrcDist (cos SrcTheta)))))
))
