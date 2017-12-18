  MODULE mod_poisson

  PRIVATE
  PUBLIC :: poisxy1, poisxy2

  CONTAINS

      SUBROUTINE poisxy1 ( xio, mx,ny, xmsg,                             &
  &                        guess, gtype, nscan, epsx, relc, xout)

      IMPLICIT NONE

      INTEGER,INTENT(in)                      :: mx, ny, nscan, guess, gtype
      INTEGER                                 :: mscan, ier
      REAL(8),INTENT(in)                      :: xmsg, epsx, relc
      REAL(8), DIMENSION(mx,ny),INTENT(in)    :: xio
      REAL(8), DIMENSION(mx,ny),INTENT(out)   :: xout
      INTEGER                                 :: nmsg, n, m
      REAL(8)                                 :: resmax

      ier  = 0
      nmsg = 0
      DO n=1,ny
        DO m=1,mx
           IF (xio(m,n).eq.xmsg) nmsg = nmsg + 1
        ENDDO 
      ENDDO 

! if no missing values return the original array

      IF (nmsg.ne.0)  THEN
      CALL poisxy2(xio,mx,ny,xmsg,nscan,epsx,relc,guess,gtype,           &
  &                resmax,mscan,xout)
      ENDIF

      END SUBROUTINE


      SUBROUTINE poisxy2(xin,il,jl,amsg,maxscn,crit,relc,guess,gtype,    &
  &                     resmax, mscan,xout)

!=======================================================================
! Not sure of the original source. ? MOM ?
!=======================================================================
!     inputs:
!     a       = array with missing areas to be filled. 
!     il      = number of points along 1st dimension to be filled
!     jl      = number of points along 2nd dimension to be filled
!     maxscn  = maximum number of passes allowed in relaxation
!     crit    = criterion for ending relaxation before "maxscn" limit
!     relc    = relaxation constant
!     gtype   = 0 : not cyclic in x
!               1 : cyclic in x
!     guess   = 0 : use 0.0 as an initial guess
!             = 1 : at each "y" use the average values for that "y"
!                   think zonal averages
!     outputs:
!
!     a       = array with interpolated values 
!               non missing areas remain unchanged.
!     resmax  = max residual
!
!
      IMPLICIT NONE

      INTEGER,INTENT(in)                     :: il, jl, maxscn, guess, gtype
      INTEGER,INTENT(out)                    :: mscan
      REAL(8),INTENT(in)                     :: amsg, crit
      REAL(8),INTENT(out)                    :: resmax
      REAL(8),DIMENSION(il,jl),INTENT(in)    :: xin
      REAL(8),DIMENSION(il,jl),INTENT(out)   :: xout

! local
!     sor     = scratch area

      LOGICAL                  :: done
      INTEGER                  :: i, j, n, im1, ip1, jm1, jp1
      REAL(8)                  :: p25, relc, res, aavg
      REAL(8),DIMENSION(il,jl) :: sor, a

      a(:,:) = xin(:,:)
 
      p25 = 0.25d0 

      DO j=1,jl
         n    = 0
         aavg = 0.0d0
        DO i=1,il
          IF (a(i,j) .eq. amsg) THEN
              sor(i,j) = relc
          ELSE
              n        = n + 1
              aavg     = aavg+ a(i,j)
              sor(i,j) = 0.0d0
          ENDIF
        ENDDO 

        IF (n.gt.0) THEN
            aavg = aavg/n
        ENDIF

        IF (guess.eq.0) THEN
            DO i=1,il
               IF (a(i,j) .eq. amsg) a(i,j) = 0.0d0
            ENDDO
        ELSEIF (guess.eq.1) THEN
            DO i=1,il
              IF (a(i,j) .eq. amsg) a(i,j) = aavg
            ENDDO
        ENDIF

      ENDDO

!-----------------------------------------------------------------------
!     iterate until errors are acceptable.
!-----------------------------------------------------------------------
!     
      mscan = 0
100   continue
        resmax = 0.0d0
        done   = .false.
        mscan  = mscan + 1
        do j=1,jl
           jp1 = j+1
           jm1 = j-1
           if (j.eq.1 ) jm1 = 2
           if (j.eq.jl) jp1 = jl-1
          do i=1,il
!                                      only work on missing value locations
             if (sor(i,j).ne.0.0) then 
                 im1 = i-1
                 ip1 = i+1
!                                      cyclic in x           
                 if (i.eq.1  .and. gtype.eq.1) im1 = il 
                 if (i.eq.il .and. gtype.eq.1) ip1 = 1
!                                      not cyclic in x           
                 if (i.eq.1  .and. gtype.eq.0) im1 = 2
                 if (i.eq.il .and. gtype.eq.0) ip1 = il-1 
    
                 res = p25*(a(im1,j)+a(ip1,j)+a(i,jm1)+a(i,jp1)) -a(i,j)
                 res     = res*sor(i,j)
                 a(i,j)  = a(i,j) + res
                 resmax  = max(abs(res),resmax)
             end if
          end do
        end do
 
      if (resmax .le. crit .or. n.eq.maxscn)  done = .true.
 
      if (.not. done .and. mscan .lt. maxscn) go to 100
 
!     write (6,99) mscan, resmax
!  99 format (1x,'==> Extrapolated  mscan=',i4
!    &,       ' scans.  max residual=', g14.7)


      xout(:,:) = a(:,:)

      return
      END SUBROUTINE

  END MODULE
