  MODULE mod_utils

  CONTAINS

    !! Use Euler-Rodrigues formula to rotate vector
    SUBROUTINE vector_rotation(axis,theta,uin,vin,uout,vout,nx,ny,nz)

    IMPLICIT NONE

    REAL,DIMENSION(3),INTENT(in)         :: axis
    REAL,INTENT(in),DIMENSION(ny,nx)     :: theta
    REAL,INTENT(in),DIMENSION(nz,ny,nx)  :: uin,vin
    REAL,INTENT(out),DIMENSION(nz,ny,nx) :: uout,vout
    INTEGER, INTENT(in)                  :: nx,ny,nz 

    REAL,DIMENSION(3)                    :: axis_norm, vect_in, vect_out
    INTEGER                              :: ji, jj, jk
    REAL                                 :: a, b, c, d, aa, bb, cc, dd
    REAL                                 :: bc, ad, ac, ab, bd, cd
    REAL,DIMENSION(3,3)                  :: rotation_matrix

    axis_norm = axis / dot_product(axis,axis)
    
    DO ji=1,nx
      DO jj=1,ny
        DO jk=1,nz

           vect_in = (/ uin(jk,jj,ji) , vin(jk,jj,ji), 0. /)

           a = COS(theta(jj,ji) / 2.0)
           b = -axis_norm(1) * SIN(theta(jj,ji) / 2.0)
           c = -axis_norm(2) * SIN(theta(jj,ji) / 2.0)
           d = -axis_norm(3) * SIN(theta(jj,ji) / 2.0)

           aa=a*a
           bb=b*b
           cc=c*c
           dd=d*d
           bc=b*c
           ad=a*d
           ac=a*c
           ab=a*b
           bd=b*d
           cd=c*d

           rotation_matrix = transpose(reshape( (/ aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac), &
                                                   2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab), &
                                                   2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc /), shape(rotation_matrix)))


           vect_out(1) = dot_product(rotation_matrix(1,:),vect_in)
           vect_out(2) = dot_product(rotation_matrix(2,:),vect_in)
           vect_out(3) = dot_product(rotation_matrix(3,:),vect_in)

           uout(jk,jj,ji) = vect_out(1)
           vout(jk,jj,ji) = vect_out(2)

        ENDDO
      ENDDO
    ENDDO
      

    END SUBROUTINE

  END MODULE
