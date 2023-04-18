(use-output-directory)

(set! resolution 45)
(define port (open-input-file ".SimParams")) (define SimParams (read port)) (close-input-port port)


(define HoleQty (list-ref SimParams 0))
(define HoleSep (list-ref SimParams 1))
(define HoleWid (list-ref SimParams 2))
(define HoleDpt (list-ref SimParams 3))
(define TotalLen ( - (* (+ HoleQty 1) HoleSep) HoleWid))

(define GlassDpt (list-ref SimParams 4))

(define SrcDist (list-ref SimParams 5))
(define SrcTheta (list-ref SimParams 6)) ; Angle is given in degrees to be converted to radian
(set! SrcTheta (* (/ pi 180) SrcTheta))


(set! geometry-lattice (make lattice (size TotalLen 8 no-size)))  ; Sim space


; Define materials that will make a nice contour overlay when we plot dielectric function

(define mat1 (make medium (epsilon 12))) ; Will be replaced with BK7
(define mat2 (make medium (epsilon 50)))  ; Will be replaced with Au

; This is so far unused and hardcoded,
; but user should be able to define planes like this,
; in wich poynting vector flux will be integrated with time to get irradiance
(define sensorTest (volume (center 0 2 0) (size 1 1 infinity) (e1 1 1 0) (e2 -1 1 0) (e3 0 0 1)))

(set! geometry (list
    (make block
    (material mat1)
    (size infinity GlassDpt infinity )
    (center 0 (* -1 (/ (+ HoleDpt GlassDpt) 2))))
    ))

(set! geometry(
    append geometry (
    map ( lambda (n) (
    make block
    (material mat2)
    (size (- HoleSep HoleWid) HoleDpt infinity)
    (center  (- (* n HoleSep) (/ TotalLen 2)) 0))) 
    (arith-sequence 0 1 (+ HoleQty 1))
        )
    )
)

(init-fields)
(output-epsilon)
(reset-meep)

(set! mat1 BK7)
(set! mat2 Au)

(set! geometry-lattice (make lattice (size TotalLen 8 no-size)))  ; Sim space
(set! geometry (list
    (make block
    (material mat1)
    (size infinity GlassDpt infinity )
    (center 0 (* -1 (/ (+ HoleDpt GlassDpt) 2))))
    ))

(set! geometry(
    append geometry (
    map ( lambda (n) (
    make block
    (material mat2)
    (size (- HoleSep HoleWid) HoleDpt infinity)
    (center  (- (* n HoleSep) (/ TotalLen 2)) 0))) 
    (arith-sequence 0 1 (+ HoleQty 1))
        )
    )
)


(set! pml-layers (list (make pml (thickness 1.0))))


(set! sources (list
               (make source
                 (src (make continuous-src (frequency 0.85)))
                 (component Ez)
                 (center 0 (* -1 SrcDist)))
               (make source
                 (src (make continuous-src (frequency 0.85)))
                 (component Ez)
                 (center (* SrcDist (sin SrcTheta)) (* -1 (* SrcDist (cos SrcTheta)))))
))

(run-until 20
    (to-appended "ez" (at-every 0.2 output-efield-z))
    (to-appended "S-vec" (at-every 0.2 synchronized-magnetic output-poynting)))
